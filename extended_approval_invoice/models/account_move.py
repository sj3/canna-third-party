# Copyright (C) 2020 SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# Copyright 2009-2024 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountInvoice(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "extended.approval.method.field.mixin"]

    ea_method_name = "action_post"

    def button_draft(self):
        self.ea_abort_approval()
        return super().button_draft()

    def button_cancel(self):
        self.ea_cancel_approval()
        return super().button_cancel()
