# Copyright 2021 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    @api.model
    def _update_users_if_enforce_changed(self):
        self.env["res.users"].sudo().search([])._compute_exclude_from_role_policy()

    @api.model_create_multi
    def create(self, vals_list):
        r = super(IrConfigParameter, self).create(vals_list)
        if "role_policy_enforced" in r.mapped("key"):
            self._update_users_if_enforce_changed()
        return r

    def write(self, vals):
        r = super(IrConfigParameter, self).write(vals)
        if "role_policy_enforced" in r.mapped("key"):
            self._update_users_if_enforce_changed()
        return r

    def unlink(self):
        keys = self.mapped("key")
        r = super(IrConfigParameter, self).unlink()
        if "role_policy_enforced" in keys:
            self._update_users_if_enforce_changed()
        return r
