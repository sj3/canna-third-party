# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from .camt import CamtParserAdv as Parser

import logging
_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    def _parse_file(self, cr, uid, data_file, context=None):
        parser = Parser()
        try:
            _logger.debug("Try parsing with camt.")
            return parser.parse(data_file)
        except ValueError:
            # Not a camt file, returning super will call next candidate:
            _logger.debug("Statement file was not a camt file.",
                          exc_info=True)
            return super(AccountBankStatementImport, self)._parse_file(
                cr, uid, data_file, context=context)

    @api.model
    def _find_bank_account_id(self, account_number):
        res = super(AccountBankStatementImport, self)._find_bank_account_id(
            account_number)
        if not res:
            """
            Some banks put the local account number as
            identification in stead of the IBAN.
            Such a local number tends to be a subset of the IBAN
            """
            company_banks = self.env['res.partner.bank'].search(
                [('company_id', '=', self.env.user.company_id.id)])
            bank = company_banks.filtered(
                lambda r: account_number in r.acc_number.replace(' ', ''))
            if bank and len(bank) == 1:
                res = bank.id
        return res
