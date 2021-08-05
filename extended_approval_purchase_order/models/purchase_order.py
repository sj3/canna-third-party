# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020-2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class PurchaseOrder(models.Model):
    """
    PO state selection:
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    """

    _name = "purchase.order"
    _inherit = ["purchase.order", "extended.approval.method.field.mixin"]

    def button_draft(self):
        self.ea_cancel_approval()
        return super().button_draft()
