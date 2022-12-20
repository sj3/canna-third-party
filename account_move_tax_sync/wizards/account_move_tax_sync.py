# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from itertools import combinations

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AccountMoveTaxSync(models.TransientModel):
    _name = "account.move.tax.sync"
    _description = "Sync taxes on Journal Items with Tax objects"

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    move_id = fields.Many2one(comodel_name="account.move", string="Journal Entry")
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal")
    action = fields.Selection(
        selection=[("check", "Check Entries"), ("repair", "Repair Entries")],
        default="check",
        required=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    note = fields.Text(string="Notes", readonly=True)

    @api.onchange("journal_id", "company_id", "date_from", "date_to")
    def _onchange_journal_id(self):
        dom = [("company_id", "=", self.company_id.id)]
        move_dom = dom.copy()
        tax_dom = dom.copy()
        if self.date_from:
            move_dom += [("date", ">=", self.date_from)]
        if self.date_to:
            move_dom += [("date", "<=", self.date_to)]
        res = {"domain": {"move_id": move_dom, "tax_id": tax_dom}}
        if self.journal_id:
            move_dom += [("journal_id", "=", self.journal_id.id)]
            if self.journal_id.type == "sale":
                tax_dom += [("type_tax_use", "=", "sale")]
            elif self.journal_id.type == "purchase":
                tax_dom += [("type_tax_use", "=", "purchase")]
        return res

    def tax_sync(self):
        if not self._uid == self.env.ref("base.user_admin").id:
            raise UserError(_("You are not allowed to execute this Operation."))
        tax_tags = self.env["account.account.tag"].search(
            [
                ("applicability", "=", "taxes"),
                ("country_id", "=", self.company_id.country_id.id),
            ]
        )
        accounts = (
            self.with_context(dict(self.env.context, active_test=False))
            .env["account.account"]
            .search([("company_id", "=", self.company_id.id)])
        )
        tax_v59 = self.env["account.tax"].search(
            [("code", "=", "VAT-V59"), ("company_id", "=", self.company_id.id)]
        )
        tax_v82 = self.env["account.tax"].search(
            [("code", "=", "VAT-V82"), ("company_id", "=", self.company_id.id)]
        )
        wiz_dict = {
            "error_log": "",
            "error_cnt": 0,
            "warning_log": "",
            "warning_cnt": 0,
            "updates": self.env["account.move"],
            "check_account_invoice": False,
            "check_tax_code": False,
            "tax_tags": {x.id: x for x in tax_tags},
            "accounts": {x.id: x for x in accounts},
            "tax_v59": tax_v59,
            "tax_v82": tax_v82,
        }
        ams = self.move_id
        if not ams:
            am_dom = [("company_id", "=", self.company_id.id)]
            if self.date_from:
                am_dom.append(("date", ">=", self.date_from))
            if self.date_to:
                am_dom.append(("date", "<=", self.date_to))
            if self.journal_id:
                am_dom.append(("journal_id", "=", self.journal_id.id))
            ams = self.env["account.move"].search(am_dom, order="name, date")
        wiz_dict["selected_ams"] = ams
        self._check_legacy_tables(wiz_dict)
        for am in ams:
            self._sync_taxes(am, wiz_dict)

        updates = wiz_dict["updates"]
        upd_nbr = len(updates)
        self.note = "Journal Entries update count: %s" % upd_nbr
        if wiz_dict["error_cnt"]:
            self.note += "\n\n"
            self.note += "Number of errors: %s" % wiz_dict["error_cnt"]
            self.note += "\n\n"
            self.note += wiz_dict["error_log"]
        if wiz_dict["warning_cnt"]:
            self.note += "\n\n"
            self.note += "Number of warnings: %s" % wiz_dict["warning_cnt"]
            self.note += "\n\n"
            self.note += wiz_dict["warning_log"]
        if upd_nbr:
            self.note += "\n\n"
            if self.action == "check":
                self.note += "To be updated "
            else:
                self.note += "Updated "
            self.note += "Journal Entries" + ":\n"
            numbers = [
                (not x.name or x.name == "/") and "*{}".format(x.id) or x.name
                for x in updates
            ]
            self.note += ", ".join(numbers)
        module = __name__.split("addons.")[1].split(".")[0]
        result_view = self.env.ref("{}.{}_view_form_result".format(module, self._table))
        return {
            "name": _("Sync Journal Entry Taxes"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "view_id": result_view.id,
            "context": self.env.context,
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def _check_legacy_tables(self, wiz_dict):
        """
        entries created <= Odoo 12.0: check account_invoice
        entries created <= Odoo 8.0: check account_tax_code
        """
        self.env.cr.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = 'account_invoice'"
        )
        res = self.env.cr.fetchone()
        if res:
            wiz_dict["check_account_invoice"] = True

        self.env.cr.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_name = 'account_tax_code'"
        )
        res = self.env.cr.fetchone()
        if res:
            wiz_dict["check_tax_code"] = True
            self.env.cr.execute(
                "SELECT id, code FROM account_tax_code WHERE company_id = %s",
                (self.company_id.id,),
            )
            res = self.env.cr.fetchall()
            wiz_dict["tax_codes"] = {x[0]: x[1] for x in res}

        coa_ml = self.env.ref(
            "l10n_be_coa_multilang.l10n_be_coa_multilang_template",
            raise_if_not_found=False,
        )
        if self.company_id.chart_template_id == coa_ml and wiz_dict["check_tax_code"]:
            atc_2_tax = self._get_legacy_l10n_be_coa_multilang_tax_code_mappings()
            wiz_dict["atc_2_tax"] = {}
            for tc in atc_2_tax:
                tax = self.env["account.tax"].search(
                    [
                        ("code", "=", atc_2_tax[tc]),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
                wiz_dict["atc_2_tax"][tc] = tax

    def _get_legacy_l10n_be_coa_multilang_tax_code_mappings(self):
        return {
            "59": "VAT-V59",
            "61": "VAT-V61",
            "62": "VAT-V62",
            "82": "VAT-V82",
        }

    def _sync_taxes(self, am, wiz_dict):
        _logger.debug("Tax Sync Processing %s (ID: %s)", am.name, am.id)
        error_cnt = 0
        error_log = []
        am_dict = {
            "am": am,
            "ail2aml": {},
            "ait2aml": {},
            "to_update": [],
            "to_create": [],
            "aml_done": am.line_ids.filtered(lambda r: not r.balance),
        }
        if am.journal_id.type == "bank":
            self._sync_bank_entries(am_dict, wiz_dict)
        elif am.type == "entry":
            pos = False
            if "pos.order" in self.env.registry:
                pos = self._get_pos_objects(am)
            if pos:
                self._sync_pos_taxes(pos, am_dict, wiz_dict)
            else:
                self._sync_entry_taxes(am_dict, wiz_dict)
        else:
            aml_new_todo = self._sync_legacy_account_invoice(am_dict, wiz_dict)
            # for invoices created in 13.0 the _sync_legacy_account_invoice returns
            # an empty recordset, hence we create the aml_new_todo
            if not aml_new_todo and len(am_dict["aml_done"]) != len(am.line_ids):
                am_new = self.env["account.move"].new(origin=am)
                am_new.line_ids = am_new.line_ids.filtered(
                    lambda r: not r.exclude_from_invoice_tab and r.balance
                )
                am_new._recompute_tax_lines()
                sign = am.type in ("in_refund", "out_invoice") and -1 or 1
                aml_new_todo = am_new.line_ids.sorted(lambda r: sign * r.balance)
            self._sync_invoice_taxes(aml_new_todo, am_dict, wiz_dict)

        to_update = am_dict["to_update"]
        to_create = am_dict["to_create"]
        to_unlink = am.line_ids - am_dict["aml_done"]
        # ignore zero lines
        to_unlink = to_unlink.filtered(lambda r: r.balance)
        if to_unlink:
            error_cnt += 1
            error_log.append(
                ("Tax recalc wants to remove Journal Items %s") % to_unlink.ids
            )
        if to_create:
            error_cnt += 1
            vals_list = [
                {f: aml[f] for f in ["account_id", "tax_audit", "tax_line_id", "name"]}
                for aml in to_create
            ]
            error_log.append(("Tax recalc wants to create %s") % vals_list)

        if error_cnt:
            wiz_dict["error_cnt"] += error_cnt
            wiz_dict["error_log"] += (
                "Errors detected during tax recalc of %s (ID: %s)"
            ) % (am.name, am.id)
            wiz_dict["error_log"] += ":\n"
            wiz_dict["error_log"] += "\n".join(error_log)
            wiz_dict["error_log"] += "\n"

        elif to_update:
            _logger.debug(
                "Tax Sync update details:\nJournal Entry: %s (ID:%s)\n. Updates: %s",
                am.name,
                am.id,
                to_update,
            )
            if self.action == "repair":
                upd_ctx = dict(self.env.context, sync_taxes=True)
                for entry in to_update:
                    # tax_audit is a computed field hence remove from aml_updates
                    aml_updates = {
                        k: v for k, v in entry[1].items() if k != "tax_audit"
                    }
                    entry[0].with_context(upd_ctx).update(aml_updates)
            wiz_dict["updates"] |= am

    def _sync_entry_taxes(self, am_dict, wiz_dict):
        """
        Equal to _sync_invoice_taxes at this point in time for
        "general" entries created after Odoo 8.0
        """
        am = am_dict["am"]
        if wiz_dict["check_tax_code"]:
            self._update_legacy_atc_entry_taxes(am_dict, wiz_dict)
        am_new = self.env["account.move"].new(origin=am)
        am_new._recompute_tax_lines()
        self._sync_invoice_taxes(am_new.line_ids, am_dict, wiz_dict)

    def _sync_invoice_taxes(self, aml_new_todo, am_dict, wiz_dict):
        am = am_dict["am"]
        sign = am.type in ("in_invoice", "out_refund") and 1 or -1
        if am.currency_id != am.company_id.currency_id:
            amt_fld = "amount_currency"
            is_zero = am.currency_id.is_zero
        else:
            amt_fld = "balance"
            is_zero = am.company_id.currency_id.is_zero
        tax_match_fields = self._get_tax_match_fields()
        if amt_fld == "amount_currency" and "balance" in tax_match_fields:
            tax_match_fields[tax_match_fields.index("balance")] = amt_fld

        aml_new_done = self.env["account.move.line"]
        for aml_new in aml_new_todo:

            def _check_match(aml, tax_match_fields):
                for f in tax_match_fields:
                    if isinstance(aml[f], float):
                        if not is_zero(aml[f] - aml_new[f]):
                            return False
                    else:
                        if aml[f] != aml_new[f]:
                            return False
                return True

            origin = aml_new._origin
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if origin in am.line_ids and _check_match(origin, tax_match_fields):
                aml = am.line_ids.filtered(lambda r: r == origin)
            else:
                aml_todo = am.line_ids - am_dict["aml_done"]
                aml = aml_todo.filtered(lambda r: _check_match(r, tax_match_fields))
                if len(aml) != 1:
                    # fallback to lookup without account_id to cope with
                    # changed tax objects
                    match_fields_no_account = tax_match_fields[:]
                    match_fields_no_account.remove("account_id")
                    aml_no_account = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_account)
                    )
                    # limit match to same account group
                    # remark:
                    # this logic may fail for countries without standardised CoA
                    aml = aml_no_account.filtered(
                        lambda r: r.account_id.code[:3] == aml_new.account_id.code[:3]
                    )
                if len(aml) != 1:
                    # fallback to lookup with rounding diffs
                    diff = 0.01001
                    match_fields_no_balance = tax_match_fields[:]
                    match_fields_no_balance.remove(amt_fld)
                    aml_no_balance = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_balance)
                    )
                    aml = aml_no_balance.filtered(
                        lambda r: (r.balance - diff)
                        <= aml_new.balance
                        <= (r.balance + diff)
                    )
                if len(aml) != 1:
                    # fallback to lookup without account_id with rounding diffs
                    diff = 0.01001
                    match_fields_no_account_balance = match_fields_no_account[:]
                    match_fields_no_account_balance.remove(amt_fld)
                    aml_no_account_balance = aml_todo.filtered(
                        lambda r: _check_match(r, match_fields_no_account_balance)
                    )
                    # same account group
                    aml_no_account_balance = aml_no_account_balance.filtered(
                        lambda r: r.account_id.code[:3] == aml_new.account_id.code[:3]
                    )
                    aml = aml_no_account_balance.filtered(
                        lambda r: (r.balance - diff)
                        <= aml_new.balance
                        <= (r.balance + diff)
                    )
                    if not aml:
                        # The tax window may have been edited resulting
                        # in an update of the first line of a tax group
                        # by the tax group widget.
                        # We do check here the amount_by_group field
                        tax_group = aml_new.tax_line_id.tax_group_id
                        group_amount = [
                            x for x in am.amount_by_group if x[6] == tax_group.id
                        ]
                        if group_amount:
                            tax_amount = sign * group_amount[0][1]
                        aml = aml_no_account_balance.filtered(
                            lambda r: abs(r.balance - tax_amount) <= diff
                        )

            if aml and len(aml) == 1:
                am_dict["aml_done"] |= aml
                aml_new_done += aml_new
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
            else:
                am_dict["to_create"].append(aml_new_dict)
                aml_new_done += aml_new

    def _sync_pos_taxes(self, pos, am_dict, wiz_dict):
        am = am_dict["am"]
        is_zero = am.company_id.currency_id.is_zero
        if pos._name == "pos.session":
            data = pos._accumulate_amounts({})
        else:
            # pre Odoo 13.0 entry
            ps = pos.mapped("session_id")
            ctx = dict(self.env.context, account_move_tax_sync=True)
            ps_new = self.env["pos.session"].with_context(ctx).new(origin=ps)
            ps_new.order_ids = pos
            # Legacy entries are incorrectly computed as invoiced
            # hence we need to set the account_move field to False
            ps_new.order_ids.update({"account_move": False})
            data = ps_new._accumulate_amounts({})
        aml_todo = am.line_ids - am_dict["aml_done"]
        aml_todo = aml_todo.filtered(lambda r: r.balance)

        for key in data["taxes"]:
            account_id, repartition_line_id, tax_id, tag_ids = key
            amounts = data["taxes"][key]
            aml_new_dict = {
                "tax_repartition_line_id": repartition_line_id,
                "tax_line_id": tax_id,
                "tax_ids": [],
                "tag_ids": tag_ids,
                "tax_audit": False,
            }
            amls = aml_todo.filtered(
                lambda r: r.account_id.id == account_id
                and r.tax_line_id.id == tax_id
                and r.tax_repartition_line_id.id == repartition_line_id
            )
            if not amls:
                # fallback to lookup without account_id to cope with
                # changed tax objects
                amls = aml_todo.filtered(
                    lambda r: r.tax_line_id.id == tax_id
                    and r.tax_repartition_line_id.id == repartition_line_id
                )
            for aml in amls:
                aml_todo -= aml
                # tax_base_amount = aml.tax_base_amount
                if len(amls) == 1:
                    if not is_zero(aml.balance - amounts["amount_converted"]):
                        raise UserError(
                            _("Error detected during tax recalc of %s") % aml
                        )
                    tax_base_amount = -amounts["base_amount_converted"]
                else:
                    tax_base_amount = self._get_tax_base_amount(aml, am_dict, wiz_dict)
                aml_new_dict["tax_base_amount"] = tax_base_amount
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)

        for key, _amounts in data["sales"].items():
            account_id, sign, tax_keys, tag_ids = key
            tax_ids = {tax[0] for tax in tax_keys}
            aml_new_dict = {
                "tax_repartition_line_id": False,
                "tax_line_id": False,
                "tax_ids": tax_ids,
                "tag_ids": tag_ids,
                "tax_base_amount": 0.0,
                "tax_audit": False,
            }
            amls = aml_todo.filtered(
                lambda r: r.account_id.id == account_id
                and set(r.tax_ids.ids) == set(tax_ids)
            )
            if len(amls) >= 1:
                if sign == 1:  # sales
                    amls = amls.filtered(lambda r: r.balance <= 0)
                else:  # refund
                    amls = amls.filtered(lambda r: r.balance > 0)
            for aml in amls:
                aml_todo -= aml
                self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)

        check_taxes = aml_todo.filtered(lambda r: r.tax_ids or r.tax_line_id)
        if check_taxes:
            raise UserError(
                _(
                    "Error during tax recalc of '%s' (ID: %s).\n"
                    "Non-handled taxes in %s"
                )
                % (am.name, am.id, check_taxes)
            )
        am_dict["aml_done"] = am.line_ids

    def _get_tax_sync_fields(self):
        """
        We include tax_line_id and tax_repartion_line_id since these
        could be wrongly set for entries created from Odoo <= 8.0
        invoices.
        The Odoo OE migration scripts put these fields equal to one of the
        tax objects with matching tax codes.
        As a consequence Odoo 8.0 tax lines created from VAT-OUT-21-S
        may show up with e.g. tax_line_id VAT-OUT-21-G in the migrated database.
        """
        return [
            "tax_base_amount",
            "tag_ids",
            "tax_ids",
            "tax_line_id",
            "tax_repartition_line_id",
        ]

    def _get_tax_match_fields(self):
        return ["account_id", "balance", "tax_line_id", "tax_repartition_line_id"]

    def _calc_aml_updates(self, aml_new_dict, aml, am_dict, wiz_dict):
        if aml.balance == 0.0:
            return
        to_update = am_dict["to_update"]
        is_zero = aml.company_id.currency_id.is_zero
        tax_sync_fields = self._get_tax_sync_fields()
        aml_updates = {}
        for fld in tax_sync_fields:
            if aml._fields[fld].type == "many2one":
                diff_check = aml_new_dict[fld] != aml[fld].id
            elif hasattr(aml[fld], "ids"):
                diff_check = set(aml_new_dict[fld]) != set(aml[fld].ids)
            elif isinstance(aml[fld], float):
                diff_check = not is_zero(aml_new_dict[fld] - aml[fld])
            else:
                diff_check = aml_new_dict[fld] != aml[fld]
            if diff_check:
                if aml._fields[fld].type == "many2one":
                    aml_updates[fld] = aml_new_dict[fld]
                elif hasattr(aml[fld], "ids"):
                    aml_updates[fld] = [(6, 0, aml_new_dict[fld])]
                else:
                    aml_updates[fld] = aml_new_dict[fld]
        if not compare_taxaudit(aml_new_dict["tax_audit"], aml["tax_audit"]):
            # recalc tax_audit string
            aml_recalc = self.env["account.move.line"].new(origin=aml)
            aml_updates = {k: aml_updates[k] for k in aml_updates if k != "tax_audit"}
            aml_recalc.update(dict(aml_updates, debit=aml.debit, credit=aml.credit))
            if any([aml_recalc.tax_audit, aml.tax_audit]) and not compare_taxaudit(
                aml_recalc.tax_audit, aml.tax_audit
            ):
                aml_updates["tax_audit"] = aml_recalc.tax_audit
        if aml_updates:
            to_update.append((aml, aml_updates))

    def _get_aml_new_dict(self, aml_new):
        return {
            "account_id": aml_new.account_id.id,
            "name": aml_new.name,
            "tax_repartition_line_id": aml_new.tax_repartition_line_id.id,
            "tax_line_id": aml_new.tax_line_id.id,
            "debit": aml_new.debit,
            "credit": aml_new.credit,
            "balance": aml_new.balance,
            "currency_id": aml_new.currency_id.id,
            "amount_currency": aml_new.amount_currency,
            "tax_base_amount": aml_new.tax_base_amount,
            "tax_ids": aml_new.tax_ids.ids,
            "tag_ids": aml_new.tag_ids.ids,
            "tax_audit": aml_new.tax_audit,
        }

    def _get_pos_objects(self, am):
        self.env.cr.execute(
            "SELECT DISTINCT(ps.id) FROM pos_order po "
            "INNER JOIN pos_session ps on po.session_id = ps.id "
            "WHERE ps.move_id = %s",
            (am.id,),
        )
        res = self.env.cr.fetchall()
        if len(res) > 1:
            raise UserError(
                _(
                    "Data Error - multiple POS sessions linked "
                    "to a single Journal Entry.\n"
                    "Journal Entry: %s (ID: %s)"
                )
                % (am.name, am.id)
            )
        if len(res) == 1:
            return self.env["pos.session"].browse(res[0])
        elif not res:
            # The move_id field on pos.session has been introduced as from Odoo 13.0.
            # The Odoo OE migration scripts also do not create this field on
            # older sessions.
            # As a consequence we add extra logic to find the underlying orders.
            self.env.cr.execute(
                "SELECT id FROM pos_order WHERE account_move = %s", (am.id,)
            )
            res = self.env.cr.fetchall()
            if not res:
                return False
            pos_order_ids = [x[0] for x in res]
            return self.env["pos.order"].browse(pos_order_ids)

    def _sync_legacy_account_invoice(self, am_dict, wiz_dict):
        """
        Find match via account_invoice table for databases which have been
        created prior to Odoo 13.0
        """
        if wiz_dict["check_tax_code"]:
            self._repair_invoice_tax_ids(am_dict, wiz_dict)
        am = am_dict["am"]
        self.env.cr.execute(
            "SELECT id FROM account_invoice WHERE move_id = %s", (am.id,)
        )
        res = self.env.cr.fetchone()
        if not res:
            return self.env["account.move.line"]
        inv_id = res[0]

        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        aml_todo = am.line_ids.filtered(lambda r: r not in am_dict["aml_done"]).sorted(
            lambda r: sign * r.balance
        )

        self.env.cr.execute(
            "SELECT * FROM account_invoice_tax "
            "WHERE invoice_id = %s "
            "ORDER BY amount",
            (inv_id,),
        )
        aits = self.env.cr.dictfetchall()
        # Filter out zero lines. We encounter such entries
        # in the tax window when we have a corresponding zero amount
        # invoice line, e.g. product with 100% discount).
        # For diagnostic purposes we prefer at this point
        # in time the seperate filter line below.
        aits = [x for x in aits if x["amount"]]

        am_new = self.env["account.move"].new(origin=am)
        # We filter out all non-invoice lines before tax recalc.
        # This is a bit tricky since We assume that the
        # previous steps have fully corrected the invoice tab
        am_new.line_ids = am_new.line_ids.filtered(
            lambda r: not r.exclude_from_invoice_tab and r.balance
        )
        am_new._recompute_tax_lines()
        aml_new_todo = am_new.line_ids.sorted(lambda r: sign * r.balance)

        # if any([ait.get("tax_code_id") for ait in aits]):
        #     # Odoo <= 8.0 entry
        #     aml_new_todo = self._sync_legacy_account_invoice_tax_code(
        #         aits, aml_new_todo, am_dict, wiz_dict
        #    )

        aml_new_todo = self._sync_legacy_account_invoice_aits_grouped(
            aits, aml_new_todo, am_dict, wiz_dict
        )

        # Entry created by Odoo > 8.0 and < 13.0 or
        # entry created <= 8.0 but where for some reason the tax_code is gone
        aml_todo = am.line_ids - am_dict["aml_done"]
        aml_todo = aml_todo.sorted(lambda r: sign * r.balance)
        aml_new_todo_copy = aml_new_todo
        for aml_new in aml_new_todo_copy:
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if aml_new_dict["currency_id"]:
                amt_fld = "amount_currency"
                is_zero = am.currency_id.is_zero
            else:
                amt_fld = "balance"
                is_zero = am.company_id.currency_id.is_zero
            tax_line_id = aml_new_dict["tax_line_id"]
            acc_aits = [
                ait for ait in aits if ait["account_id"] == aml_new_dict["account_id"]
            ]
            for ait in acc_aits:
                aml = self.env["account.move.line"]
                if ait["tax_id"] == tax_line_id:
                    aml = aml_todo.filtered(
                        lambda r: r.account_id.id == ait["account_id"]
                        and r.tax_line_id.id == tax_line_id
                        and is_zero(r[amt_fld] - sign * ait["amount"])
                    )
                if not aml:
                    # Issue detected during upgrade of lpw_prod from 10.0 to 13.0:
                    # The tax_line_id in the converted database is wrong for
                    # intracomm acquisitions (e.g.two times VAT-IN-V82-21-EU-S whereas
                    # it should be VAT-IN-V82-21-EU-S and VAT-IN-V82-21-EU-G or even
                    # cases where 'tax_ids' or set on tax lines i.s.o. tax_line_id.
                    # Hence the script that worked during 13.0 upgrades in 2021
                    # are now failing (now = 2022-05) and more repair work is required.
                    # As a fallback we are trying to find the tax lines without
                    # comparing the tax_line_id
                    aml = aml_todo.filtered(
                        lambda r: r.account_id.id == ait["account_id"]
                        and is_zero(r[amt_fld] - sign * ait["amount"])
                    )
                # repeat logic above but now with rounding diff
                if not aml:
                    diff = 0.01001
                    if ait["tax_id"] == tax_line_id:
                        aml = aml_todo.filtered(
                            lambda r: r.account_id.id == ait["account_id"]
                            and r.tax_line_id.id == tax_line_id
                            and (
                                r[amt_fld] - diff
                                <= sign * ait["amount"]
                                <= r[amt_fld] + diff
                            )
                        )
                    if not aml:
                        aml = aml_todo.filtered(
                            lambda r: r.account_id.id == ait["account_id"]
                            and (
                                r[amt_fld] - diff
                                <= sign * ait["amount"]
                                <= r[amt_fld] + diff
                            )
                        )
                if len(aml) == 1:
                    am_dict["aml_done"] |= aml
                    aml_todo -= aml
                    aml_new_todo -= aml_new
                    self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                    break
        return aml_new_todo

    def _sync_legacy_account_invoice_aits_grouped(
        self, aits, aml_new_todo, am_dict, wiz_dict
    ):
        """
        Handle issues detected during upgrade of lpw_prod from 10.0 to 13.0:
        We remark that the Odoo migration service 8.0 -> 10.0 (dd. 2017-12) has
        in some cases recreated the 'account.invoice.tax' lines and hence dropped
        the no longer existing tax codes in this table.
        The logic to repair those old 8.0 entries via the tax code
        doesn't work for these cases hence we try to fix those by
        grouping key account_id, amount
        """
        self._sync_legacy_account_invoice_manual_aits(aits, am_dict, wiz_dict)

        # repeat match and update logic up to rounding diff of 2 cent
        diff_start = 0.00001  # alternative for is_zero method
        diff_step = 0.01
        for cnt in range(3):
            diff = diff_start + cnt * diff_step

            # step 1: match on a non-grouped basis
            aits_todo = [
                x for x in aits if x["id"] not in am_dict["ait2aml"] and not x["manual"]
            ]
            for ait in aits_todo:
                aml_new_todo = self._update_aml_from_aits(
                    [ait], diff, aml_new_todo, am_dict, wiz_dict
                )

            # step 2: match via grouping key
            aits_todo = [
                x for x in aits if x["id"] not in am_dict["ait2aml"] and not x["manual"]
            ]
            aml_new_todo = self._update_aml_from_aits(
                aits_todo, diff, aml_new_todo, am_dict, wiz_dict
            )

            # Finally we try to match via combinations.
            # We observe cases where a subset of the lines are grouped
            # because they originally did have same tax_code_id but
            # different base_code_id.
            # Since we observe cases where the tax codes have gone
            # we can try to cover this by iterating through the
            # combinations.
            aits_todo = [
                x for x in aits if x["id"] not in am_dict["ait2aml"] and not x["manual"]
            ]
            tax_acc_ids = {x["account_id"] for x in aits_todo}
            for tax_acc_id in tax_acc_ids:
                tax_acc_aits = [
                    ait for ait in aits_todo if ait["account_id"] == tax_acc_id
                ]
                # we have already tried single match and fully grouped
                for i in range(1, len(tax_acc_aits) - 1):
                    aits_combinations = combinations(tax_acc_aits, i + 1)
                    for entry in aits_combinations:
                        aml_new_todo = self._update_aml_from_aits(
                            entry, diff, aml_new_todo, am_dict, wiz_dict
                        )

        aml_new_todo = self._sync_legacy_account_invoice_unmatched_aits(
            aits, aml_new_todo, am_dict, wiz_dict
        )
        return aml_new_todo

    def _sync_legacy_account_invoice_manual_aits(self, aits, am_dict, wiz_dict):
        """
        Sync the 'manual' taxes added to the invoice tax window
        """
        am = am_dict["am"]
        aml_todo = am.line_ids - am_dict["aml_done"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        if am.currency_id != am.company_id.currency_id:
            amt_fld = "amount_currency"
            is_zero = am.currency_id.is_zero
        else:
            amt_fld = "balance"
            is_zero = am.company_id.currency_id.is_zero
        aits_manual = [x for x in aits if x["manual"]]
        for ait in aits_manual:
            aml = aml_todo.filtered(
                lambda r: r.account_id.id == ait["account_id"]
                and is_zero(r[amt_fld] - sign * ait["amount"])
            )
            if len(aml) != 1:
                continue
            aml_new_dict = self._get_aml_new_dict(aml)
            is_refund = am.type in ("in_refund", "out_refund")
            tax = self.env["account.tax"]
            if ait.get("tax_code_id"):
                tax_code = wiz_dict["tax_codes"][ait["tax_code_id"]]
                tax = wiz_dict["atc_2_tax"].get(tax_code)
            elif ait.get("tax_id"):
                tax = self.env["account.tax"].browse(ait["tax_id"])
            if tax:
                tax_tags = tax.get_tax_tags(is_refund, "base")
                if set(aml_new_dict["tag_ids"]) != set(tax_tags.ids):
                    aml_new_dict["tag_ids"] = tax_tags.ids
            aml_new_dict["tax_ids"] = []
            self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
            aml_todo -= aml
            am_dict["aml_done"] |= aml
            am_dict["ait2aml"][ait["id"]] = aml.id

    def _update_aml_from_aits(self, aits, diff, aml_new_todo, am_dict, wiz_dict):
        am = am_dict["am"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        if am.currency_id != am.company_id.currency_id:
            amt_fld = "amount_currency"
        else:
            amt_fld = "balance"
        aml_todo = am.line_ids - am_dict["aml_done"]
        aml_todo = aml_todo.sorted(lambda r: sign * r.balance)

        tax_acc_ids = {x["account_id"] for x in aits}
        for tax_acc_id in tax_acc_ids:
            tax_acc_aits = [x for x in aits if x["account_id"] == tax_acc_id]
            tax_amount = sign * sum([ait["amount"] for ait in tax_acc_aits])
            aml = aml_todo.filtered(
                lambda r: r.account_id.id == tax_acc_id
                and r.exclude_from_invoice_tab
                and abs(tax_amount - getattr(r, amt_fld)) <= diff
            )
            if len(aml) != 1:
                continue
            aml_new_tax_acc = aml_new_todo.filtered(
                lambda r: r.account_id.id == tax_acc_id and r.exclude_from_invoice_tab
            )
            if not aml_new_tax_acc:
                continue

            aml_new_dict = self._get_aml_new_dict(aml_new_tax_acc[0])
            aml_new_tax_amount = sum(aml_new_tax_acc.mapped(amt_fld))
            if abs(tax_amount - aml_new_tax_amount) <= diff:
                for aml in aml_todo.filtered(
                    lambda r: r.account_id.id == tax_acc_id
                    and r.exclude_from_invoice_tab
                ):
                    aml_amt = getattr(aml, amt_fld)
                    if abs(aml_amt - tax_amount) <= diff:
                        am_dict["aml_done"] |= aml
                        for x in tax_acc_aits:
                            am_dict["ait2aml"][x["id"]] = aml.id
                        if aml.tax_ids:
                            aml_new_dict["tax_ids"] = []
                        self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                        aml_new_todo -= aml_new_tax_acc
                        break

            # We do not always have a grouping but it's tricky since it depends
            # on the Odoo version at invoice creation time.
            # E.g. we may have no grouping in case of different originator tax
            for aml in aml_todo.filtered(lambda r: r.account_id.id == tax_acc_id):
                for orig_tax_id in [x["tax_id"] for x in tax_acc_aits]:
                    orig_tax_acc_aits = [
                        ait for ait in tax_acc_aits if ait["tax_id"] == orig_tax_id
                    ]
                    tax_amount = sign * sum(
                        [ait["amount"] for ait in orig_tax_acc_aits]
                    )
                    aml_new_tax_acc = aml_new_todo.filtered(
                        lambda r: r.account_id.id == tax_acc_id
                        and r.exclude_from_invoice_tab
                        and r.tax_line_id.id == orig_tax_id
                    )
                    aml_new_tax_amount = sum(aml_new_tax_acc.mapped(amt_fld))
                    if abs(tax_amount - aml_new_tax_amount) <= diff:
                        aml_new_dict = self._get_aml_new_dict(aml_new_tax_acc[0])
                        # if is_zero(aml.balance - tax_amount):
                        aml_amt = getattr(aml, amt_fld)
                        if abs(aml_amt - tax_amount) <= diff:
                            am_dict["aml_done"] |= aml
                            for x in tax_acc_aits:
                                am_dict["ait2aml"][x["id"]] = aml.id
                            if aml.tax_ids:
                                aml_new_dict["tax_ids"] = []
                            self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                            aml_new_todo -= aml_new_tax_acc
                            break

            aml_todo = am.line_ids - am_dict["aml_done"]

        return aml_new_todo

    def _sync_legacy_account_invoice_unmatched_aits(  # noqa: C901
        self, aits, aml_new_todo, am_dict, wiz_dict
    ):
        """
        Let's double check if there are still unmatched ait tax lines and
        add some logic to match them anyhow.
        """
        am = am_dict["am"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        if am.currency_id != am.company_id.currency_id:
            is_zero = am.currency_id.is_zero
            amt_fld = "amount_currency"
        else:
            is_zero = am.company_id.currency_id.is_zero
            amt_fld = "balance"
        aits_todo = [x for x in aits if x["id"] not in am_dict["ait2aml"]]

        tax_acc_ids = {x["account_id"] for x in aits_todo}
        for tax_acc_id in tax_acc_ids:
            aml_new_tax_acc = self.env["account.move.line"]
            tax_acc_aits = [x for x in aits_todo if x["account_id"] == tax_acc_id]
            ana_acc_ids = {x["account_analytic_id"] for x in aits_todo}
            if len(ana_acc_ids) > 1:
                # there is a functional bug in the Odoo 13.0 tax engine for
                # non-deductible taxes:
                # If multiple supplier invoice lines have the ND same tax object but
                # a different analytic account, than you would expect the ND taxes
                # to respect those different analytic account but the tax engine
                # ignores this and sums them up.
                # As a consequence the previous matching logic did fail, we cover
                # this use case here.
                for ana_acc_id in ana_acc_ids:
                    ana_acc_aits = [
                        x
                        for x in tax_acc_aits
                        if x["account_analytic_id"] == ana_acc_id
                    ]
                    ait_tax_amount = sign * sum([x["amount"] for x in ana_acc_aits])
                    aml = am.line_ids.filtered(
                        lambda r: r.account_id.id == tax_acc_id
                        and r.exclude_from_invoice_tab
                        and (r.analytic_account_id.id or None) == ana_acc_id
                        and r.id not in am_dict["ait2aml"].values()
                    )

                    if len(aml) != 1:
                        continue

                    aml_new_tax_acc = aml_new_todo.filtered(
                        lambda r: r.account_id.id == tax_acc_id
                        and r.exclude_from_invoice_tab
                    )
                    if len(aml_new_tax_acc) > 1:
                        # This case can happen when we have different originator taxes
                        # with the same tax tags.
                        # In Odoo <= V8.0 tax window entries on the same tax_code_id
                        # were grouped into a single tax aml.
                        # A concrete use case is a vendor invoice with purchases
                        # of 21% and 6% VAT.
                        # We check if the tax tags of all aml_new_tax_acc are equal
                        # and use the most important one to correct the tax aml.
                        tag_set_list = [set(x.tag_ids.ids) for x in aml_new_tax_acc]
                        if tag_set_list.count(tag_set_list[0]) == len(tag_set_list):
                            aml_new_tax_acc = aml_new_tax_acc.sorted(
                                lambda r: abs(r.balance), reverse=True
                            )[0]
                        else:
                            # we need to refine the logic if we encounter this use case
                            _logger.error(
                                "NotImplementedError detected in method "
                                "'_sync_legacy_account_invoice_unmatched_aits' "
                                "while processing %s (ID: %s).",
                                am.name,
                                am.id,
                            )
                            raise NotImplementedError
                    am_dict["aml_done"] |= aml
                    for ana_acc_ait in ana_acc_aits:
                        am_dict["ait2aml"][ana_acc_ait["id"]] = aml.id
                    aml_new_dict = self._get_aml_new_dict(aml_new_tax_acc)
                    if aml.tax_ids:
                        aml_new_dict["tax_ids"] = []
                    self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)

                    # add warning message when deviation seems too big for rounding diff
                    max_diff = 0.10
                    aml_tax_amount = getattr(aml, amt_fld)
                    tax_amount_diff = ait_tax_amount - aml_tax_amount
                    check = abs(tax_amount_diff) <= max_diff
                    if not check:
                        warn_msg = (
                            "Large deviation of %s detected between legacy invoice "
                            "tax window and corresponding Journal Item with ID %s"
                        ) % (round(tax_amount_diff, 2), aml.id)
                        wiz_dict["warning_cnt"] += 1
                        wiz_dict["warning_log"] += (
                            "Warnings during tax recalc of %s (ID: %s)"
                        ) % (am.name, am.id,)
                        wiz_dict["warning_log"] += ":\n"
                        wiz_dict["warning_log"] += warn_msg
                        wiz_dict["warning_log"] += "\n"

            aml_new_todo -= aml_new_tax_acc

        aits_todo = [x for x in aits if x["id"] not in am_dict["ait2aml"]]
        tax_acc_ids = {x["account_id"] for x in aits_todo}
        for tax_acc_id in tax_acc_ids:
            tax_acc_aits = [x for x in aits_todo if x["account_id"] == tax_acc_id]
            tax_code_ids = [x.get("tax_code_id") for x in tax_acc_aits]
            for tax_code_id in tax_code_ids:
                tax_acc_code_aits = [
                    x for x in tax_acc_aits if x.get("tax_code_id") == tax_code_id
                ]
                ait_tax_amount = sign * sum([x["amount"] for x in tax_acc_code_aits])
                aml = am.line_ids.filtered(
                    lambda r: r.account_id.id == tax_acc_id
                    and r.exclude_from_invoice_tab
                )
                if aml:
                    # we have one or more tax_lines on the same general account
                    # hence we are could here be in a case where the accounting entry
                    # has been manually adjusted by the accountant to match with the
                    # received supplier invoice
                    if len(aml) != 1:
                        # refine via originator tax
                        for tax_acc_ait in tax_acc_code_aits:
                            aml_refined = aml.filtered(
                                lambda r: r.tax_line_id.id == tax_acc_ait["tax_id"]
                            )
                            if len(aml_refined) == 1:
                                aml = aml_refined
                                break
                    if len(aml) != 1:
                        # filter out via ait2aml
                        aml_refined = aml.filtered(
                            lambda r: r.id not in am_dict["ait2aml"].values()
                        )
                        if len(aml_refined) == 1:
                            aml = aml_refined
                    if len(aml) != 1:
                        # filter via amount
                        aml_refined = aml.filtered(
                            lambda r: is_zero(r[amt_fld] - ait_tax_amount)
                        )
                        if len(aml_refined) == 1:
                            aml = aml_refined
                    if len(aml) != 1:
                        wiz_dict["error_cnt"] += 1
                        wiz_dict["error_log"] += (
                            "Errors detected during tax recalc of %s (ID: %s)"
                        ) % (am.name, am.id)
                        wiz_dict["error_log"] += ":\n"
                        wiz_dict["error_log"] += (
                            "No matching account.move.line found for "
                            "account_invoice_tax IDS %s.\n"
                        ) % [x["id"] for x in tax_acc_code_aits]
                        if aml:
                            wiz_dict["error_log"] += (
                                "Unmatched aml IDS on same account: %s"
                            ) % aml.ids
                        wiz_dict["error_log"] += "\n"
                        break

                    aml_new_tax_acc = aml_new_todo.filtered(
                        lambda r: r.account_id.id == tax_acc_id
                        and r.exclude_from_invoice_tab
                    )
                    if len(aml_new_tax_acc) > 1:
                        # refine by amount to cover the case of two tax lines on
                        # the same general account which have not been summed because
                        # of different tax code in Odoo 8.0
                        aml_new_tax_acc_refined = aml_new_tax_acc.filtered(
                            lambda r: is_zero(r[amt_fld] - ait_tax_amount)
                        )
                        if len(aml_new_tax_acc_refined) == 1:
                            aml_new_tax_acc = aml_new_tax_acc_refined
                    if len(aml_new_tax_acc) > 1:
                        # This case can happen when we have different originator taxes
                        # with the same tax tags.
                        # In Odoo <= V8.0 tax window entries on the same tax_code_id
                        # were grouped into a single tax aml.
                        # A concrete use case is a vendor invoice with purchases
                        # of 21% and 6% VAT.
                        # We check if the tax tags of all aml_new_tax_acc are equal
                        # and use the most important one to correct the tax aml.
                        tag_set_list = [set(x.tag_ids.ids) for x in aml_new_tax_acc]
                        if tag_set_list.count(tag_set_list[0]) == len(tag_set_list):
                            aml_new_todo -= aml_new_tax_acc
                            aml_new_tax_acc = aml_new_tax_acc.sorted(
                                lambda r: abs(r.balance), reverse=True
                            )[0]
                        else:
                            # we need to refine the logic if we encounter this use case
                            _logger.error(
                                "NotImplementedError detected in method "
                                "'_sync_legacy_account_invoice_unmatched_aits' "
                                "while processing %s (ID: %s).",
                                am.name,
                                am.id,
                            )
                            raise NotImplementedError
                    am_dict["aml_done"] |= aml
                    for tax_acc_ait in tax_acc_code_aits:
                        am_dict["ait2aml"][tax_acc_ait["id"]] = aml.id
                    aml_new_dict = self._get_aml_new_dict(aml_new_tax_acc)
                    if aml_new_tax_acc:
                        if aml.tax_ids:
                            aml_new_dict["tax_ids"] = []
                        self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                        aml_new_todo -= aml_new_tax_acc

                    # add warning message when deviation seems too big for rounding diff
                    max_diff = 0.10
                    aml_tax_amount = getattr(aml, amt_fld)
                    tax_amount_diff = ait_tax_amount - aml_tax_amount
                    check = abs(tax_amount_diff) <= max_diff
                    if not check:
                        warn_msg = (
                            "Large deviation of %s detected between legacy invoice "
                            "tax window and corresponding Journal Item with ID %s"
                        ) % (round(tax_amount_diff, 2), aml.id)
                        wiz_dict["warning_cnt"] += 1
                        wiz_dict["warning_log"] += (
                            "Warnings during tax recalc of %s (ID: %s)"
                        ) % (am.name, am.id,)
                        wiz_dict["warning_log"] += ":\n"
                        wiz_dict["warning_log"] += warn_msg
                        wiz_dict["warning_log"] += "\n"

        return aml_new_todo

    def _repair_invoice_tax_ids(self, am_dict, wiz_dict):
        """
        We observe that the OE migration service sometimes copies the
        invoice_line_tax_id to the wrong Journal Item tax_ids for 8.0 legacy invoices.
        This method repairs these mistakes.

        We also observe that sometimes non-invoice lines have not been marked as
        such (e.g. account receivable/payable) and vice versa.
        """
        am = am_dict["am"]
        upd_ctx = dict(self.env.context, sync_taxes=True)
        arap = am.line_ids.filtered(
            lambda r: r.account_internal_type in ("payable", "receivable")
        )
        am_dict["aml_done"] |= arap
        arap_to_fix = arap.filtered(lambda r: not r.exclude_from_invoice_tab)
        for aml in arap_to_fix:
            wiz_dict["updates"] |= am
            if self.action == "repair":
                aml.with_context(upd_ctx)["exclude_from_invoice_tab"] = True
                aml.flush(["exclude_from_invoice_tab"])

        self.env.cr.execute(
            "SELECT id FROM account_invoice WHERE move_id = %s", (am.id,)
        )
        res = self.env.cr.fetchone()
        if not res:
            return False

        inv_id = res[0]
        self.env.cr.execute(
            "SELECT * FROM account_move_line "
            "WHERE move_id = %s "
            "AND account_internal_type NOT IN ('payable', 'receivable') ",
            (am.id,),
        )
        amls = self.env.cr.dictfetchall()
        self.env.cr.execute(
            "SELECT * FROM account_invoice_line "
            "WHERE invoice_id = %s "
            "AND price_subtotal != 0 "
            "AND display_type IS NULL",
            (inv_id,),
        )
        ails = self.env.cr.dictfetchall()
        match_fields = self._get_ail_2_aml_match_fields()
        matched_amls = []
        unmatched_ails = []
        for ail in ails:
            matches = self._update_aml_from_ail(
                ail, amls, match_fields, am_dict, wiz_dict
            )
            if not matches:
                unmatched_ails.append(ail)
            else:
                [matched_amls.append(x) for x in matches if x not in matched_amls]

        unmatched_amls = [x for x in amls if x not in matched_amls]
        unmatched_ails = self._update_unmatched_amls_from_unmatched_ails_hook(
            unmatched_ails, unmatched_amls, am_dict, wiz_dict
        )
        unmatched_ails = self._update_unmatched_amls_from_unmatched_ails_grouped(
            unmatched_ails, unmatched_amls, match_fields, am_dict, wiz_dict
        )

        if unmatched_ails:
            # Fallback to match without product_id
            match_fields_no_product = match_fields.copy()
            del match_fields_no_product["product_id"]
            matched_ails = []
            for ail in unmatched_ails:
                matches = self._update_aml_from_ail(
                    ail, unmatched_amls, match_fields_no_product, am_dict, wiz_dict
                )
                if matches:
                    matched_ails.append(ail)
                    [matched_amls.append(x) for x in matches if x not in matched_amls]
            if matched_ails:
                unmatched_ails = [x for x in unmatched_ails if x not in matched_ails]

        if unmatched_ails:
            wiz_dict["error_cnt"] += 1
            wiz_dict["error_log"] += (
                "Errors detected during tax recalc of %s (ID: %s)"
            ) % (am.name, am.id)
            wiz_dict["error_log"] += ":\n"
            wiz_dict["error_log"] += (
                "tax_ids repair failed for legacy invoice %s (ID: %s).\n"
                "No corresponding account.move.line found for "
                "account_invoice_line IDS %s"
            ) % (am.name, am.id, [x["id"] for x in unmatched_ails])
            wiz_dict["error_log"] += "\n"

        elif am_dict["to_update"]:
            _logger.debug(
                "Tax Sync update details:\nJournal Entry: %s (ID:%s)\n. Updates: %s",
                am.name,
                am.id,
                am_dict["to_update"],
            )
            if self.action == "repair":
                [x[0].with_context(upd_ctx).update(x[1]) for x in am_dict["to_update"]]
                [x[0].flush(x[1].keys()) for x in am_dict["to_update"]]
            am_dict["to_update"] = []
            wiz_dict["updates"] |= am

    def _update_unmatched_amls_from_unmatched_ails_hook(
        self, unmatched_ails, unmatched_amls, am_dict, wiz_dict
    ):
        """
        hook to allow custom specific logic to refine matching
        """
        return unmatched_ails

    def _update_aml_from_ail(self, ail, amls, match_fields, am_dict, wiz_dict):
        am = am_dict["am"]
        to_update = am_dict["to_update"]
        self.env.cr.execute(
            "SELECT tax_id FROM account_invoice_line_tax WHERE invoice_line_id = %s",
            (ail["id"],),
        )
        ail_tax_ids = [x[0] for x in self.env.cr.fetchall()]
        if am.currency_id != am.company_id.currency_id:
            is_zero = am.currency_id.is_zero
            amt_fld = "amount_currency"
        else:
            is_zero = am.company_id.currency_id.is_zero
            amt_fld = "balance"
        sign = am.type in ("in_invoice", "out_refund") and 1 or -1
        matches = [
            aml
            for aml in amls
            if all([ail[k] == aml[match_fields[k]] for k in match_fields])
            and is_zero(ail["price_subtotal"] - sign * (aml[amt_fld] or 0.0))
            and aml["id"] not in am_dict["ail2aml"].values()
        ]
        if matches:
            match = matches[0]
            upd_vals = {}
            aml_id = match["id"]
            self._update_ail2aml(aml_id, [ail["id"]], am_dict, wiz_dict)
            self.env.cr.execute(
                "SELECT account_tax_id FROM account_move_line_account_tax_rel "
                "WHERE account_move_line_id = %s",
                (aml_id,),
            )
            aml_tax_ids = [x[0] for x in self.env.cr.fetchall()]
            if set(ail_tax_ids) != set(aml_tax_ids):
                upd_vals["tax_ids"] = [(6, 0, ail_tax_ids)]
            for fld in ["quantity", "price_subtotal", "discount", "price_total"]:
                if ail[fld] != match[fld]:
                    upd_vals[fld] = ail[fld]
            if match["exclude_from_invoice_tab"]:
                upd_vals["exclude_from_invoice_tab"] = False
            if upd_vals:
                aml = am.line_ids.filtered(lambda r: r.id == aml_id)
                found = False
                for entry in to_update:
                    if entry[0] == aml:
                        entry[1].update(upd_vals)
                        found = True
                        break
                if not found:
                    to_update.append((aml, upd_vals))
        return matches and [matches[0]]

    def _update_unmatched_amls_from_unmatched_ails_grouped(  # noqa: C901
        self, unmatched_ails, unmatched_amls, match_fields, am_dict, wiz_dict
    ):
        """
        match group of ails with single aml for journals wich
        have been configured via the 'group_invoice_lines' flag
        """
        am = am_dict["am"]
        to_update = am_dict["to_update"]
        if am.currency_id != am.company_id.currency_id:
            is_zero = am.currency_id.is_zero
            amt_fld = "amount_currency"
        else:
            is_zero = am.company_id.currency_id.is_zero
            amt_fld = "balance"
        sign = am.type in ("in_invoice", "out_refund") and 1 or -1

        for aml in unmatched_amls:
            matched_ails = [
                ail
                for ail in unmatched_ails
                if all([aml[match_fields[k]] == ail[k] for k in match_fields])
                and ail["id"] not in am_dict["ail2aml"]
            ]
            if not matched_ails:
                continue
            if not is_zero(
                sum([x["price_subtotal"] for x in matched_ails]) - sign * aml[amt_fld]
            ):
                continue
            # check if all matched_ails have the same tax_ids
            check_taxes = True
            for i, ail in enumerate(matched_ails):
                self.env.cr.execute(
                    """
                SELECT tax_id FROM account_invoice_line_tax WHERE invoice_line_id = %s
                    """,
                    (ail["id"],),
                )
                ail_tax_ids = [x[0] for x in self.env.cr.fetchall()]
                if i == 0:
                    ail_tax_ids_set = set(ail_tax_ids)
                else:
                    if set(ail_tax_ids) != ail_tax_ids_set:
                        check_taxes = False
            if not check_taxes:
                continue

            # we now have a match via the grouping logic
            upd_vals = {}
            self._update_ail2aml(
                aml["id"], [x["id"] for x in matched_ails], am_dict, wiz_dict
            )
            self.env.cr.execute(
                "SELECT account_tax_id FROM account_move_line_account_tax_rel "
                "WHERE account_move_line_id = %s",
                (aml["id"],),
            )
            aml_tax_ids = [x[0] for x in self.env.cr.fetchall()]
            if ail_tax_ids_set != set(aml_tax_ids):
                upd_vals["tax_ids"] = [(6, 0, ail_tax_ids)]
            # In case of grouped invoice lines where the upgrade service
            # failed to match or recreate those we may encounter different
            # price_unit and discount values in the old invoice lines.
            # We solve this by setting the average price_unit and we use
            # the discount of the first invoice line
            quantity = sum([x["quantity"] for x in matched_ails]) or 1.0
            discount = matched_ails[0]["discount"] or 0
            price_unit = (sign * aml[amt_fld] / quantity) / (1 - discount)
            price_subtotal = sum([x["price_subtotal"] for x in matched_ails])
            price_total = sum([x["price_total"] for x in matched_ails])
            if aml["quantity"] != quantity:
                upd_vals["quantity"] = quantity
            if aml["discount"] != discount:
                upd_vals["discount"] = discount
            if not is_zero((aml["price_unit"] or 0) - price_unit):
                upd_vals["price_unit"] = price_unit
            if not is_zero((aml["price_subtotal"] or 0) - price_subtotal):
                upd_vals["price_subtotal"] = price_subtotal
            if not is_zero((aml["price_total"] or 0) - price_total):
                upd_vals["price_total"] = price_total
            if upd_vals:
                aml = am.line_ids.filtered(lambda r: r.id == aml["id"])
                found = False
                for entry in to_update:
                    if entry[0] == aml:
                        entry[1].update(upd_vals)
                        found = True
                        break
                if not found:
                    to_update.append((aml, upd_vals))

        unmatched_ails = [
            x for x in unmatched_ails if x["id"] not in am_dict["ail2aml"]
        ]
        return unmatched_ails

    def _get_ail_2_aml_match_fields(self):
        """
        The fields in this dictionary are combined with the price_subtotal
        field to find the matching aml.
        """
        return {
            "account_id": "account_id",
            "product_id": "product_id",
            "account_analytic_id": "analytic_account_id",
        }

    def _sync_legacy_account_invoice_tax_code_DEPRECATED(  # noqa: C901
        self, aits, aml_new_todo, am_dict, wiz_dict
    ):
        """
        This method is no longer called. The logic has been replaced by
        the _sync_legacy_account_invoice_aits_grouped method.
        """
        am = am_dict["am"]
        sign = am.type in ("in_refund", "out_invoice") and -1 or 1
        is_zero = am.company_id.currency_id.is_zero

        aml_todo = am.line_ids - am_dict["aml_done"]
        if len(aml_todo) != len(aml_new_todo):
            # We had a grouping by tax code in Odoo 8 versus
            # grouping by tax_line_id in later versions.
            # Since we don't want to touch the general ledger we
            # need to choose which tax object we will put on the
            # tax line and hence need a method that can be inherited
            # by a customer specific module.
            for aml in aml_todo:
                aml_new_todos = aml_new_todo.filtered(
                    lambda r: r.tax_line_id and r.account_id == aml.account_id
                )
                if not aml_new_todos:
                    continue
                check_balance = sum(aml_new_todos.mapped("balance")) - aml.balance
                match = False
                if is_zero(check_balance):
                    match = True
                else:
                    diff = 0.01001
                    if abs(check_balance) <= diff:
                        match = True
                    else:
                        aml_new_todos = aml_new_todo.filtered(
                            lambda r: r.tax_line_id
                            and r.account_id.code[:2] == aml.account_id.code[:2]
                        )
                        check_balance = (
                            sum(aml_new_todos.mapped("balance")) - aml.balance
                        )
                        if abs(check_balance) <= diff:
                            match = True
                if match:
                    taxes = aml_new_todos.mapped("tax_line_id")
                    if len(taxes) > 1:
                        tax = self._get_preferred_tax(aits, taxes, am_dict, wiz_dict)
                    else:
                        tax = taxes
                    aml_new_dict = self._get_aml_new_dict(
                        aml_new_todos.filtered(lambda r: r.tax_line_id == tax)[0]
                    )
                    aml_new_dict["tax_base_amount"] = sum(
                        aml_new_todos.mapped("tax_base_amount")
                    )
                    aml_new_dict["tax_ids"] = False
                    self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
                    am_dict["aml_done"] |= aml
                    aml_todo -= aml
                    aml_new_todo -= aml_new_todos

            # We observe missing 'tax_line_id' or 'tax_repartition_line_id'
            # in Journal Items converted by the Odoo OE migration service
            # in case of legacy entries created from tax children.
            # The _recompute_tax_lines creates new Journal Items in such cases
            # in stead of updating the existing ones.
            # We have added logic here to find and update the existing Journal Items.
            if len(aml_todo) != len(aml_new_todo):
                aml_todo = am.line_ids.filtered(
                    lambda r: r.exclude_from_invoice_tab
                    and r.balance  # ignore the legacy zero and 'display_type' lines
                    and r.account_internal_type not in ("receivable", "payable")
                    and r not in am_dict["aml_done"]
                )
                aml_new_no_origin = aml_new_todo.filtered(lambda r: not r._origin)
                aml_new_todo |= aml_new_no_origin
                aml_new_todo = aml_new_todo.sorted(lambda r: sign * r.balance)
        aml_new_done = self.env["account.move.line"]
        for aml_new in aml_new_todo:
            if aml_new in aml_new_done:
                continue
            done = False
            aml_new_dict = self._get_aml_new_dict(aml_new)
            if aml_new_dict["currency_id"]:
                amt_fld = "amount_currency"
                is_zero = am.currency_id.is_zero
            else:
                amt_fld = "balance"
                is_zero = am.company_id.currency_id.is_zero
            tag_ids = aml_new_dict["tag_ids"]
            # we observe high rounding differences for invoices
            # with many lines -> diff of 2 cent may not always be sufficient
            diff = 0.02001
            aits_todo = [
                x for x in aits if x["id"] not in am_dict["ait2aml"] and not x["manual"]
            ]
            for ait in aits_todo:
                if ait.get("tax_code_id"):
                    tax_code = wiz_dict["tax_codes"][ait["tax_code_id"]]
                    tag_names = (
                        tag_ids and "".join(aml_new.mapped("tag_ids.name")) or ""
                    )
                    if tax_code not in tag_names:
                        continue
                aits_group = [
                    x
                    for x in aits_todo
                    if x["tax_code_id"] == ait["tax_code_id"]
                    and x["base_code_id"] == ait["base_code_id"]
                    and x["account_id"] == ait["account_id"]
                ]
                tax_amount = sum([x["amount"] for x in aits_group])
                if not tax_amount:
                    continue
                aml = aml_todo.filtered(
                    lambda r: is_zero(r[amt_fld] - sign * tax_amount)
                    and r.account_id.id == ait["account_id"]
                )
                if not aml:
                    # Odoo 8.0 allowed to modify the accounting entries linked
                    # to the invoice. Some accountants (mis)used this feature
                    # to correct rounding differences in the tax lines.
                    # Hence we perform here a second lookup with approximate
                    # match on amount
                    aml = aml_todo.filtered(
                        lambda r: -diff <= (r[amt_fld] - sign * tax_amount) <= diff
                        and r.account_id.id == ait["account_id"]
                    )
                # TODO: refactor this code since we should first check for
                # exact matches and only afterwards find the associated aml_new
                if aml:
                    if len(aml) == 1 and is_zero(aml[amt_fld] - sign * tax_amount):
                        diff_2c = 0.02001  # cope with rounding differences up to 2 cent
                        aml_new_match = (aml_new_todo - aml_new_done).filtered(
                            lambda r: r.account_id == aml.account_id
                            and abs(r[amt_fld] - sign * tax_amount) <= diff_2c
                        )
                        if len(aml_new_match) == 1:
                            aml_new_dict = self._get_aml_new_dict(aml_new_match)
                            aml_new_done |= aml_new_match
                            for x in aits_group:
                                am_dict["ait2aml"][x["id"]] = aml.id
                            done = True
                    elif aml_new.account_id == aml.account_id and (
                        aml_new[amt_fld] - diff
                        <= sign * tax_amount
                        <= aml_new[amt_fld] + diff
                    ):
                        aml_new_done |= aml_new
                        for x in aits_group:
                            am_dict["ait2aml"][x["id"]] = aml.id
                        done = True
                    else:
                        acc_group = aml[0].account_id.code[:2]
                        aml_new_group = (aml_new_todo - aml_new_done).filtered(
                            lambda r: r.tag_ids.ids == tag_ids
                            and r.account_id.code[:2] == acc_group
                        )
                        tax_amount_new = sum(aml_new_group.mapped(amt_fld))
                        if is_zero(tax_amount_new - sign * tax_amount):
                            aml_new_dict = self._get_aml_new_dict(aml_new_group[0])
                            aml_new_done |= aml_new_group
                            for x in aits_group:
                                am_dict["ait2aml"][x["id"]] = aml.id
                            done = True
                        else:
                            if (
                                tax_amount_new - diff
                                <= sign * tax_amount
                                <= tax_amount_new + diff
                            ):
                                aml_new_dict = self._get_aml_new_dict(aml_new_group[0])
                                aml_new_done |= aml_new_group
                                for x in aits_group:
                                    am_dict["ait2aml"][x["id"]] = aml.id
                                done = True

                    base_amount = sum([x["base_amount"] or 0.0 for x in aits_group])
                    aml_new_dict["tax_base_amount"] = base_amount
                    for l in aml:
                        aml_new_dict["tax_ids"] = False
                        self._calc_aml_updates(aml_new_dict, l, am_dict, wiz_dict)
                    am_dict["aml_done"] |= aml
                    aml_todo -= aml
                if done:
                    break

        # add support for the 'manual' taxes added to the invoice tax window
        aits_manual = [ait for ait in aits if ait["manual"] and ait["tax_code_id"]]
        for ait in aits_manual:
            aml = aml_todo.filtered(
                lambda r: r.account_id.id == ait["account_id"]
                and is_zero(r[amt_fld] - sign * ait["amount"])
            )
            if len(aml) != 1:
                continue
            tax_code = wiz_dict["tax_codes"][ait["tax_code_id"]]
            tax = wiz_dict["atc_2_tax"].get(tax_code)
            is_refund = am.type in ("in_refund", "out_refund")
            tax_tags = tax.get_tax_tags(is_refund, "base")
            aml_new_dict = self._get_aml_new_dict(aml)
            if set(aml_new_dict["tag_ids"]) != set(tax_tags.ids):
                aml_new_dict["tag_ids"] = tax_tags.ids
            aml_new_dict["tax_ids"] = False
            self._calc_aml_updates(aml_new_dict, aml, am_dict, wiz_dict)
            if aml.tax_ids:
                upd_vals = {"tax_ids": [(5,)]}
                found = False
                for to_update in am_dict["to_update"]:
                    if to_update[0] == aml:
                        to_update[1].update(upd_vals)
                        found = True
                        break
                if not found:
                    am_dict["to_update"].append((aml, upd_vals))
            aml_todo -= aml
            am_dict["aml_done"] |= aml
            am_dict["ait2aml"][ait["id"]] = aml.id

        aml_new_todo -= aml_new_done
        return aml_new_todo

    def _get_preferred_tax(self, aits, taxes, am_dict, wiz_dict):
        """
        We had a grouping by tax code in Odoo 8 versus
        grouping by tax_line_id in later versions.
        Since we don't want to touch the general ledger we
        need to choose which tax object we will put on the
        tax line and hence need a method that can be inherited
        by a customer specific module.
        By default we return the tax with the highest ID.
        """
        taxes = taxes.sorted(lambda r: r.id, reverse=True)
        return taxes[0]

    def _sync_bank_entries(self, am_dict, wiz_dict):
        if wiz_dict["check_tax_code"]:
            self._sync_legacy_atc_bank_entries(am_dict, wiz_dict)
        # call method to convert entries created after upgrade to >8.0
        self._sync_legacy_bank_entries(am_dict, wiz_dict)

    def _sync_legacy_atc_bank_entries(self, am_dict, wiz_dict):
        """
        Add tax object to legacy entries with Odoo <= 8.0 tax codes
        in financial journals.
        """
        to_update = am_dict["to_update"]
        am = am_dict["am"]
        self.env.cr.execute(
            "SELECT id, tax_code_id FROM account_move_line WHERE move_id = %s",
            (am.id,),
        )
        res = self.env.cr.dictfetchall()
        for entry in res:
            aml = am.line_ids.filtered(lambda r: r.id == entry["id"])
            tc = wiz_dict["tax_codes"].get(entry["tax_code_id"])
            tax = tc and wiz_dict["atc_2_tax"].get(tc)
            if tax and aml.tax_ids != tax:
                to_update.append((aml, {"tax_ids": tax}))
                wiz_dict["updates"] |= am
                am_dict["aml_done"] |= aml

    def _sync_legacy_bank_entries(self, am_dict, wiz_dict):
        """
        Replace tax_line_id for V59 and tax_ids for V82 by tax tags.
        Cf. changes in l10n_be_coda_advanced for taxes on bank cost.
        """
        to_update = am_dict["to_update"]
        am = am_dict["am"]
        tax_v59 = wiz_dict["tax_v59"]
        tax_v82 = wiz_dict["tax_v82"]
        amls = am.line_ids.filtered(
            # originator tax used in coda_advanced up to Odoo 12
            lambda r: r.tax_line_id == tax_v59
            or r.tax_ids in (tax_v82, tax_v59)
            and not r.tag_ids
            and r not in am_dict["aml_done"]
        )
        for aml in amls:
            tax = aml.tax_line_id or aml.tax_ids
            tag = tax.get_tax_tags(False, "base")
            aml_updates = {
                "tax_ids": [(6, 0, tax.ids)],
                "tag_ids": [(6, 0, tag.ids)],
                "tax_line_id": False,
            }
            wiz_dict["updates"] |= am
            to_update.append((aml, aml_updates))
        am_dict["aml_done"] |= am.line_ids

    def _update_legacy_atc_entry_taxes(self, am_dict, wiz_dict):
        """
        Add tax tag corresponding to Odoo <= 8.0 tax code in general journals.
        """
        am = am_dict["am"]
        to_update = am_dict["to_update"]
        self.env.cr.execute(
            "SELECT id, tax_code_id FROM account_move_line WHERE move_id = %s",
            (am.id,),
        )
        res = self.env.cr.dictfetchall()
        for entry in res:
            upd_vals = {}
            aml = am.line_ids.filtered(lambda r: r.id == entry["id"])
            am_dict["aml_done"] |= aml
            tc = wiz_dict["tax_codes"].get(entry["tax_code_id"])
            if not tc:
                continue
            tag_dom = [("name", "=", "+%s" % tc), ("applicability", "=", "taxes")]
            tag = self.env["account.account.tag"].search(tag_dom)
            if not tag:
                tag_dom = [("name", "=", "+%sD" % tc), ("applicability", "=", "taxes")]
                tag = self.env["account.account.tag"].search(tag_dom)
            tax = wiz_dict["atc_2_tax"].get(tc) or self.env["account.tax"]
            # remove taxes which have been set incorrectly by the
            # Odoo OE migration service
            if set(aml.tax_ids.ids) != set(tax.ids):
                upd_vals["tax_ids"] = [(6, 0, tax.ids)]
            if aml.tax_line_id:
                upd_vals["tax_line_id"] = False
            if len(tag) == 1:
                if set(aml.tag_ids.ids) != set(tag.ids):
                    upd_vals["tag_ids"] = [(6, 0, tag.ids)]
            else:
                wiz_dict["error_cnt"] += 1
                error_log = (
                    "No unique Tax Tag found for legacy Tax Code %s (ID: %s)."
                ) % (tc, entry["tax_code_id"])
                wiz_dict["error_log"] += (
                    "Errors detected during tax recalc of %s (ID: %s)"
                ) % (am.name, am.id)
                wiz_dict["error_log"] += ":\n"
                wiz_dict["error_log"] += error_log
                wiz_dict["error_log"] += "\n"
            if upd_vals:
                to_update.append((aml, upd_vals))

    def _get_tax_base_amount(self, aml, am_dict, wiz_dict):
        """
        We try to find the tax_base_amls via reverse lookup.
        """
        am = am_dict["am"]
        tax_base_amount = 0.0
        tax_base_amls = am.line_ids.filtered(
            lambda r: aml.tax_line_id.id in r.tax_ids.ids
            and r.product_id == aml.product_id
        )
        if len(tax_base_amls) == 1:
            return -tax_base_amls.balance

        if aml.balance <= 0:  # sales
            tax_base_amls = tax_base_amls.filtered(lambda r: r.balance <= 0)
        else:  # refund
            tax_base_amls = tax_base_amls.filtered(lambda r: r.balance > 0)
        if len(tax_base_amls) == 1:
            return -tax_base_amls.balance

        tax = aml.tax_line_id
        if tax.amount_type == "percent":
            pct = (tax.amount * aml.tax_repartition_line_id.factor_percent) / 100
            factor = pct / 100.0
            tax_base_amount = aml.balance / factor
            for i in range(len(tax_base_amls)):
                to_check = combinations(tax_base_amls, i + 1)
                for entry in to_check:
                    # we observe rather large diff in reverse calc
                    # in historical databases
                    diff = 0.0
                    for _j in range(10):
                        diff += 0.01
                        tax_base = sum([x.balance for x in entry])
                        if (
                            (tax_base_amount - diff)
                            <= tax_base
                            <= (tax_base_amount + diff)
                        ):
                            tax_base_amls = self.env["account.move.line"]
                            for tax_base_aml in entry:
                                tax_base_amls += tax_base_aml
                            return -sum(tax_base_amls.mapped("balance"))
        warn_msg = ("tax_base_amount calculation failed for Journal Item %s") % aml.id
        wiz_dict["warning_cnt"] += 1
        wiz_dict["warning_log"] += ("Warnings during tax recalc of %s (ID: %s)") % (
            am.name,
            am.id,
        )
        wiz_dict["warning_log"] += ":\n"
        wiz_dict["warning_log"] += warn_msg
        wiz_dict["warning_log"] += "\n"

        return tax_base_amount or aml.tax_base_amount

    def _update_ail2aml(self, aml_id, ail_ids, am_dict, wiz_dict):
        ail2aml = am_dict["ail2aml"]
        for ail_id in ail_ids:
            if ail2aml.get(ail_id) and ail2aml[ail_id] != aml_id:
                raise UserError(
                    _(
                        "Programming Error detected while processing Journal Entry %s, "
                        "Journal Item %s.\n"
                        "Inconsistent ail2aml"
                    )
                    % (am_dict["am"].name, aml_id)
                )
            ail2aml[ail_id] = aml_id


def normalize_taxaudit(val):
    for i in reversed(val):
        if i in [".", ","]:
            decimal_separator = i
            break
    if decimal_separator == ".":
        val = val.replace(",", "")
    else:
        val = val.replace(".", "").replace(",", ".")
    return val.replace(" ", "")


def compare_taxaudit(val1, val2):
    val1 = val1 and normalize_taxaudit(val1)
    val2 = val2 and normalize_taxaudit(val2)
    return val1 == val2
