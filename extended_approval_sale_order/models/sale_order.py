# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    """
    SO state selection:
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    """

    _name = "sale.order"
    _inherit = ["sale.order", "extended.approval.method.field.mixin"]

    ea_method_name = "action_confirm"

    def button_draft(self):
        self.ea_cancel_approval()
        return super().button_draft()
