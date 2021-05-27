# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SalesTarget(models.Model):
    _name = "sales.target"
    _inherit = ["sales.target", "extended.approval.method.field.mixin"]

    ea_method_name = "target_confirm"

    def target_set_to_draft(self):
        self.ea_cancel_approval()
        return super().target_set_to_draft()
