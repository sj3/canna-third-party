# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.addons.account_bank_statement_import.parserlib \
    import BankTransaction as BankTransactionBase
from openerp.addons.account_bank_statement_import.parserlib \
    import BankStatement as BankStatementBase

import logging
_logger = logging.getLogger(__name__)


class BankTransaction(BankTransactionBase):

    @property
    def execution_date(self):
        """property getter"""
        return self['date']

    @execution_date.setter
    def execution_date(self, execution_date):
        """property setter"""
        self['date'] = execution_date

    @property
    def value_date(self):
        """property getter"""
        return self['val_date']

    @value_date.setter
    def value_date(self, value_date):
        """property setter"""
        self['val_date'] = value_date

    def __init__(self):
        super(BankTransaction, self).__init__()
        self.note = ''


class BankStatement(BankStatementBase):

    # Replace the parse_statement method to use BankTransaction class
    # defined in this module.
    # TODO: PR to banking-addons to facilitate inheritance.
    def create_transaction(self):
        """Create and append transaction.

        This should only be called after statement_id has been set, because
        statement_id will become part of the unique transaction_id.
        """
        transaction = BankTransaction()
        self['transactions'].append(transaction)
        # Fill default id, but might be overruled
        transaction['unique_import_id'] = (
            self.statement_id + str(len(self['transactions'])).zfill(4))
        return transaction
