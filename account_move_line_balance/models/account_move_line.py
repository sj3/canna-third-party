# -*- coding: utf-8 -*-
# Copyright (c) 2013-2015 Noviat nv/sa (www.noviat.com).
# Copyright 2020 Onestein BV (www.onestein.nl)

from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    absolute_balance = fields.Float(
        compute="_compute_balance",
        string="Absolute Amount",
        store=True,
        help="Absolute Amount in Company Currency",
    )
    signed_balance = fields.Float(
        compute="_compute_balance",
        string="Balance",
        store=True,
        help="Balance in Company Currency",
    )

    @api.depends("debit", "credit")
    def _compute_balance(self):
        for aml in self:
            balance = aml.debit - aml.credit
            aml.absolute_balance = abs(balance)
            aml.signed_balance = balance
