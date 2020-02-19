# Copyright 2020 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResRole(models.Model):
    _name = "res.role"
    _description = "Role"
    _inherit = ["mail.thread"]
    _sql_constraints = [
        ("code_company_uniq", "unique (code, company_id)", "The code must be unique !")
    ]

    name = fields.Char(required=True)
    code = fields.Char(required=True, size=5)
    group_id = fields.Many2one(
        comodel_name="res.groups", readonly=True, ondelete="restrict"
    )
    acl_ids = fields.One2many(
        comodel_name="res.role.acl", inverse_name="role_id", string="ACL Items"
    )
    modifier_rule_ids = fields.One2many(
        comodel_name="web.modifier.rule",
        inverse_name="role_id",
        string="Web Modifier Rules",
    )
    menu_ids = fields.Many2many(
        comodel_name="ir.ui.menu",
        relation="res_role_menu_rel",
        column1="role_id",
        column2="menu_id",
        string="Menu Items",
    )
    act_window_ids = fields.Many2many(
        comodel_name="ir.actions.act_window",
        relation="res_role_act_window_rel",
        column1="role_id",
        column2="act_window_id",
        string="Window Actions",
    )
    act_server_ids = fields.Many2many(
        comodel_name="ir.actions.server",
        relation="res_role_act_server_rel",
        column1="role_id",
        column2="act_server_id",
        string="Server Actions",
    )
    act_report_ids = fields.Many2many(
        comodel_name="ir.actions.report",
        relation="res_role_act_report_rel",
        column1="role_id",
        column2="act_report_id",
        string="Report Actions",
    )
    user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="res_role_users_rel",
        column1="role_id",
        column2="uid",
        string="Users",
    )
    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self._default_company_id(),
    )

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    @api.model
    def create(self, vals):
        role = super().create(vals)
        role._create_role_group()
        for f in ["menu_ids", "act_window_ids", "act_server_ids", "act_report_ids"]:
            if f in vals and vals[f][0][2]:
                getattr(role, f).write({"groups_id": [(4, role.group_id.id)]})
        return role

    def _create_role_group(self):
        categ = self.env.ref("role_policy.ir_module_category_role")
        group_vals = {
            "role": True,
            "name": self.code,
            "category_id": categ.id,
            "users": [(6, 0, self.user_ids.ids)],
        }
        self.group_id = self.env["res.groups"].create(group_vals)

    def write(self, vals):
        for role in self:
            if vals.get("code"):
                if role.code != vals["code"] and role.acl_ids:
                    raise UserError(_("You are not allowed to update the code."))
            if "user_ids" in vals:
                role.group_id.write({"users": vals["user_ids"]})
            todo = []
            for f in ["menu_ids", "act_window_ids", "act_server_ids", "act_report_ids"]:
                if f in vals:
                    for entry in vals[f]:
                        if entry[0] == 6:
                            getattr(role, f).write(
                                {"groups_id": [(3, role.group_id.id)]}
                            )
                            if entry[2]:
                                todo.append(f)
                        else:
                            raise NotImplementedError
        res = super().write(vals)
        for f in todo:
            getattr(role, f).write({"groups_id": [(4, role.group_id.id)]})
        return res

    def unlink(self):
        role_groups = self.mapped("group_id")
        res = super().unlink()
        role_groups.unlink()
        return res
