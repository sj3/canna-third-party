# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging
import os
import time

import xlrd

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class RolePolicyImport(models.TransientModel):
    _name = "role.policy.import"
    _description = "Import Role Policy"

    policy_data = fields.Binary(string="File", required=True)
    policy_fname = fields.Char(string="Filename")
    file_type = fields.Selection(
        selection="_selection_file_type", default=lambda self: self._default_file_type()
    )
    codepage = fields.Char(
        string="Code Page",
        default=lambda self: self._default_codepage(),
        help="Code Page of the system that has generated the file.",
    )
    sheet = fields.Selection(
        selection="_selection_sheet",
        help="Specify the Excel sheet."
        "\nIf not specified all sheets will be imported.",
    )
    warning = fields.Text(readonly=True)
    note = fields.Text("Log")

    @api.model
    def _selection_file_type(self):
        return [("xls", "xls"), ("xlsx", "xlsx")]

    @api.model
    def _default_file_type(self):
        return "xlsx"

    @api.model
    def _selection_sheet(self):
        return [
            ("acl", "Role ACLs"),
            ("menu", "Menu Items"),
            ("act_window", "Window Actions"),
            ("act_server", "Server Actions"),
            ("act_report", "Report Actions"),
            ("modifier_rule", "View Modifier Rules"),
            # ('record_rule', 'Record Rules'),
        ]

    @api.model
    def _default_codepage(self):
        return "utf-16le"

    @api.onchange("policy_fname")
    def _onchange_policy_fname(self):
        if not self.policy_fname:
            return
        name, ext = os.path.splitext(self.policy_fname)
        ext = ext[1:]
        if ext not in ["xls", "xlsx"]:
            self.warning = _(
                "<b>Incorrect file format !</b>"
                "<br>Only files of type csv and xls(x) are supported."
            )
            return
        else:
            self.file_type = ext
            self.warning = False

    @api.onchange("sheet")
    def _onchange_sheet(self):
        self.warning = False

    def role_policy_import(self):
        time_start = time.time()
        role = self.env["res.role"].browse(self.env.context["active_id"])
        data = base64.decodestring(self.policy_data)
        if self.file_type in ["xls", "xlsx"]:
            err_log = self._read_xls(data, role)
        else:
            raise NotImplementedError
        if self.warning:
            view = self.env.ref("role_policy.role_policy_import_view_form")
            return {
                "name": _("Import File"),
                "res_id": self.id,
                "view_type": "form",
                "view_mode": "form",
                "res_model": "role.policy.import",
                "view_id": view.id,
                "target": "new",
                "type": "ir.actions.act_window",
                "context": self.env.context,
            }

        if err_log:
            self.note = err_log
            result_view = self.env.ref(
                "role_policy.role_policy_import_view_form_result"
            )
            return {
                "name": _("Role Policy Import result"),
                "res_id": self.id,
                "view_type": "form",
                "view_mode": "form",
                "res_model": "role.policy.import",
                "view_id": result_view.id,
                "target": "new",
                "type": "ir.actions.act_window",
            }
        else:
            import_time = time.time() - time_start
            _logger.warn("Role %s import time = %.3f seconds", role.name, import_time)
            return {"type": "ir.actions.act_window_close"}

    def _read_xls(self, data, role):
        all_sheets = [x[0] for x in self._selection_sheet()]
        if self.sheet:
            sheets = [self.sheet]
            start = all_sheets.index(self.sheet)
        else:
            sheets = all_sheets
            start = 0
        err_log = ""
        wb = xlrd.open_workbook(file_contents=data)
        for i, sheet_name in enumerate(sheets, start=start):
            sheet = wb.sheet_by_index(i)
            sheet_err_log = getattr(self, "_read_{}".format(sheet_name))(sheet, role)
            if sheet_err_log:
                if err_log:
                    err_log += "\n\n"
                err_log += _("Errors detected while importing sheet '%s'.") % sheet.name
                err_log += "\n\n" + sheet_err_log
        return err_log

    def _read_acl(self, sheet, role):  # noqa: C901
        header = ["Name", "Model", "Read", "Write", "Create", "Delete"]
        headerline = sheet.row_values(0)
        err_log = self._check_sheet_header(sheet, header, headerline)
        if err_log:
            return err_log
        unlink_pos = len(header)
        unlink_column = len(headerline) > unlink_pos and headerline[unlink_pos] in [
            "Delete Entry",
            "Unlink",
        ]
        to_unlink = self.env["res.role.acl"]
        to_create = []

        for ri in range(1, sheet.nrows):
            ln = sheet.row_values(ri)
            if not ln or ln[0] and ln[0][0] == "#" or not any(ln):
                continue
            line_errors = []
            model_name = ln[1].strip()
            if model_name in self.env:
                model_id = self.env["ir.model"]._get_id(model_name)
            else:
                line_errors.append(_("Model '%s' does not exist.") % model_name)
                if err_log:
                    err_log += "\n\n"
                err_log = self._format_line_errors(ln, line_errors)
                continue

            vals = {"role_id": role.id, "model_id": model_id}
            line_action = False
            role_acl = role.acl_ids.filtered(lambda r: r.model_id.model == model_name)
            if unlink_column:
                unlink = ln[unlink_pos]
                if unlink not in ["X", "x", ""]:
                    line_errors.append(
                        _(
                            "Incorrect value '%s' for Column 'Delete Entry'. "
                            "The value should be 'X' or empty."
                        )
                        % unlink
                    )
                if unlink:
                    if not role_acl:
                        line_errors.append(
                            _(
                                "Incorrect value '%s' for Column 'Delete Entry'. "
                                "You cannot remove a Role ACL which doesn't exist."
                            )
                            % unlink
                        )
                    else:
                        line_action = "delete"
                        to_unlink += role_acl
            if not role_acl:
                line_action = "create"
            for ci, fld in enumerate(
                ["perm_read", "perm_write", "perm_create", "perm_unlink"], start=2
            ):
                cell = sheet.cell(ri, ci)
                if cell.ctype == xlrd.XL_CELL_TEXT:
                    ln[ci] = cell.value
                elif cell.ctype == xlrd.XL_CELL_NUMBER:
                    is_int = cell.value % 1 == 0.0
                    if is_int:
                        ln[ci] = str(int(cell.value))
                    else:
                        ln[ci] = str(cell.value)
                if ln[ci] not in ["0", "1"]:
                    line_errors.append(
                        _(
                            "Incorrect value '%s'for field '%s'. "
                            "The value should be '0' or '1'."
                        )
                        % (ln[ci], fld)
                    )
                val = ln[ci] == "1" and True or False
                vals[fld] = val
                if line_action != "delete":
                    if getattr(role_acl, fld) != val:
                        line_action = "write"
            if line_action == "write":
                to_unlink += role_acl
            if line_action in ["create", "write"]:
                if vals not in to_create:
                    to_create.append(vals)
                else:
                    line_errors.append(_("Duplicate entry.") % ln)
            if line_errors:
                if err_log:
                    err_log += "\n\n"
                err_log = self._format_line_errors(ln, line_errors)

        if not err_log:
            to_unlink.unlink()
            self.env["res.role.acl"].create(to_create)
        return err_log

    def _read_menu(self, sheet, role):
        header = ["Menu", "External Identifier"]
        return self._read_m2m_sheet(sheet, role, header)

    def _read_act_window(self, sheet, role):
        header = ["Window Action", "External Identifier"]
        return self._read_m2m_sheet(sheet, role, header)

    def _read_act_server(self, sheet, role):
        header = ["Server Action", "External Identifier"]
        return self._read_m2m_sheet(sheet, role, header)

    def _read_act_report(self, sheet, role):
        header = ["Report Action", "External Identifier"]
        return self._read_m2m_sheet(sheet, role, header)

    def _read_m2m_sheet(self, sheet, role, header):
        headerline = sheet.row_values(0)
        err_log = self._check_sheet_header(sheet, header, headerline)
        if err_log:
            return err_log
        unlink_pos = len(header)
        unlink_column = len(headerline) > unlink_pos and headerline[unlink_pos] in [
            "Delete Entry",
            "Unlink",
        ]
        fld = sheet.name.split(" ")[0].lower()
        if fld == "menu":
            fld = fld + "_ids"
        else:
            fld = "act_" + fld + "_ids"
        role_fld_ids = getattr(role, fld).ids
        to_remove_ids = []
        to_add_ids = []

        for ri in range(1, sheet.nrows):
            ln = sheet.row_values(ri)
            if not ln or ln[0] and ln[0][0] == "#" or not any(ln):
                continue
            line_errors = []
            fld_id = self._read_xml_id(ln[1], line_errors)

            if unlink_column:
                unlink = ln[unlink_pos]
                if unlink not in ["X", "x", ""]:
                    line_errors.append(
                        _(
                            "Incorrect value '%s' for Column 'Delete Entry'. "
                            "The value should be 'X' or empty."
                        )
                        % unlink
                    )
                if unlink:
                    if fld_id not in role_fld_ids:
                        line_errors.append(
                            _(
                                "Incorrect value '%s' for Column 'Delete Entry'. "
                                "You cannot remove a Menu Item which doesn't exist."
                            )
                            % unlink
                        )
                    else:
                        to_remove_ids.append(fld_id)
            if fld_id not in role_fld_ids:
                to_add_ids.append(fld_id)

            if line_errors:
                if err_log:
                    err_log += "\n\n"
                err_log = self._format_line_errors(ln, line_errors)

        if not err_log:
            updates = [(3, x) for x in to_remove_ids] + [(4, x) for x in to_add_ids]
            if updates:
                setattr(role, fld, updates)

        return err_log

    def _read_modifier_rule(self, sheet, role):  # noqa: C901
        header = [
            "Model",
            "Prio",
            "View",
            "View Id",
            "View Type",
            "Element",
            "Remove",
            "Invisible",
            "Readonly",
            "Required",
            "Sequence",
        ]
        headerline = sheet.row_values(0)
        err_log = self._check_sheet_header(sheet, header, headerline)
        if err_log:
            return err_log
        unlink_pos = len(header)
        unlink_column = len(headerline) > unlink_pos and headerline[unlink_pos] in [
            "Delete Entry",
            "Unlink",
        ]
        to_unlink = self.env["web.modifier.rule"]
        to_create = []

        for ri in range(1, sheet.nrows):
            ln = sheet.row_values(ri)
            if not ln or ln[0] and ln[0][0] == "#" or not any(ln):
                continue
            line_errors = []

            model_name = ln[0].strip()
            if model_name in self.env:
                model_id = self.env["ir.model"]._get_id(model_name)
            else:
                line_errors.append(_("Model '%s' does not exist.") % model_name)
                if err_log:
                    err_log += "\n\n"
                err_log = self._format_line_errors(ln, line_errors)
                continue
            prio = self._read_integer(
                ln[1], "Prio", line_errors, required=True, positive=True
            )
            view_id = self._read_integer(
                ln[3], "View Id", line_errors, required=False, positive=True
            )
            view_type = ln[4].strip() or False
            element = ln[5].strip() or False
            cell = sheet.cell(ri, 6)
            remove = cell.value
            if cell.ctype == xlrd.XL_CELL_TEXT:
                remove = cell.value.strip()
            elif cell.ctype == xlrd.XL_CELL_NUMBER:
                is_int = cell.value % 1 == 0.0
                if is_int:
                    remove = int(cell.value)
                else:
                    remove = str(cell.value)
            if remove not in [0, 1, ""]:
                line_errors.append(
                    _(
                        "Incorrect value '%s'for field '%s'. "
                        "The value should be '0' or '1'."
                    )
                    % (ln[6], "Remove")
                )
            vals = {
                "role_id": role.id,
                "model_id": model_id,
                "priority": prio,
                "view_id": view_id,
                "view_type": view_type,
                "element": element,
                "remove": remove and True or False,
            }
            for ci, fld in enumerate(["invisible", "readonly", "required"], start=7):
                cell = sheet.cell(ri, ci)
                if cell.ctype == xlrd.XL_CELL_TEXT:
                    val = cell.value.strip()
                elif cell.ctype == xlrd.XL_CELL_NUMBER:
                    is_int = cell.value % 1 == 0.0
                    if is_int:
                        val = str(int(cell.value))
                    else:
                        val = str(cell.value).strip()
                else:
                    val = str(ln[ci])
                vals["modifier_{}".format(fld)] = val or False
            match_vals = {k: v for k, v in vals.items() if k != "role_id"}

            def rule_filter(rule):
                match = True
                for k, val in match_vals.items():
                    rule_val = getattr(rule, k)
                    if k[-3:] == "_id":
                        rule_val = rule_val.id
                    if rule_val != val:
                        match = False
                        break
                return match

            rule = role.modifier_rule_ids.filtered(rule_filter)
            if len(rule) > 1:
                line_errors.append(
                    _(
                        "Multiple matching rules found in the 'Web Modifier Rules'.\n"
                        "CF. rules %s."
                    )
                    % rule
                )
            if unlink_column:
                unlink = ln[unlink_pos]
                if unlink not in ["X", "x", ""]:
                    line_errors.append(
                        _(
                            "Incorrect value '%s' for Column 'Delete Entry'. "
                            "The value should be 'X' or empty."
                        )
                        % unlink
                    )
                if unlink:
                    if not rule:
                        line_errors.append(
                            _(
                                "Incorrect value '%s' for Column 'Delete Entry'. "
                                "You cannot remove a Web Modifier Rule "
                                "which doesn't exist."
                            )
                            % unlink
                        )
                    else:
                        to_unlink += rule

            sequence = self._read_integer(
                ln[10], "Sequence", line_errors, required=True, positive=True
            )
            vals["sequence"] = sequence

            if not rule:
                if vals not in to_create:
                    to_create.append(vals)

            if line_errors:
                if err_log:
                    err_log += "\n\n"
                err_log = self._format_line_errors(ln, line_errors)

        if not err_log:
            if to_unlink:
                to_unlink.unlink()
            if to_create:
                self.env["web.modifier.rule"].create(to_create)
        return err_log

    def _check_sheet_header(self, sheet, header, headerline):
        err_log = ""
        if headerline[: len(header)] != header:
            err_log = _(
                "Error while reading sheet '%s':\n"
                "Incorrect sheet header.\n"
                "The first line of your sheet should contain the "
                "following column names: %s"
            ) % (sheet.name, header)
        return err_log

    def _read_integer(self, val, col, line_errors, required=True, positive=True):
        int_err = _(
            "Incorrect value for Column '%s'. The value should be an Integer%s."
        ) % (col, positive and " > 0" or "")
        res = val
        if res:
            try:
                res = int(val)
            except Exception:
                line_errors.append(int_err)
        if positive and res and res <= 0:
            line_errors.append(int_err)
        if required and not res:
            line_errors.append(_("Missing Value for Column '%s'.") % col)
        return res or False

    def _read_xml_id(self, val, line_errors):
        rec = self.env.ref(val, raise_if_not_found=False)
        if not rec:
            line_errors.append(_("Incorrect value for Column 'External Identifier'."))
        return rec and rec.id or False

    def _format_line_errors(self, ln, line_errors):
        err_log = _("Error while processing line %s:\n") % ln
        err_log += "\n".join(line_errors)
        return err_log
