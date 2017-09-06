# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    hr_expense = fields.Boolean(
        string='HR Expense Journal',
        help="Set this flag to allow the booking of "
             "expenses in this Journal.")
