# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrderGroup(models.Model):
    _name = "sale.order.group"
    _inherit = ["sale.order.group", "extended.approval.method.field.mixin"]

    ea_method_name = "button_confirm"

    def button_draft(self):
        self.ea_cancel_approval()
        return super().button_draft()
