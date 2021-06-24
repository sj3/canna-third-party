# Copyright 2018-2021 Onestein B.V.
# Copyright 2021 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPaymentOrder(models.Model):
    _name = "account.payment.order"
    _inherit = ["account.payment.order", "extended.approval.method.field.mixin"]

    ea_method_name = "draft2open"

    def cancel2draft(self):
        self.ea_cancel_approval()
        return super().cancel2draft()
