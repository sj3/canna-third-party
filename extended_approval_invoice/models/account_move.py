# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "extended.approval.method.field.mixin"]

    ea_signal = "action_post"

    def button_cancel(self):
        self.ea_cancel_approval()
        return super().button_cancel()
