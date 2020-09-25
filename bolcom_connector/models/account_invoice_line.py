# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import fields, models


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    bolcom_transaction_fee = fields.Float()
