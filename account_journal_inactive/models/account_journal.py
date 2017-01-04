# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import fields, models


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    active = fields.Boolean(default=True)
