# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from openerp.addons.account_bank_statement_import_camt.camt \
    import CamtParser as Parser
from openerp import _
from .parserlib import BankStatement

import logging
_logger = logging.getLogger(__name__)


class CamtParserAdv(Parser):

    # Replace the parse_statement method to use BankStatement class
    # defined in this module.
    # TODO: PR to banking-addons to facilitate inheritance.
    def parse_statement(self, ns, node):
        """Parse a single Stmt node."""
        statement = BankStatement()
        self.add_value_from_node(
            ns, node, [
                './ns:Acct/ns:Id/ns:IBAN',
                './ns:Acct/ns:Id/ns:Othr/ns:Id',
            ], statement, 'local_account'
        )
        self.add_value_from_node(
            ns, node, './ns:Id', statement, 'statement_id')
        self.add_value_from_node(
            ns, node, './ns:Acct/ns:Ccy', statement, 'local_currency')
        (statement.start_balance, statement.end_balance) = (
            self.get_balance_amounts(ns, node))
        transaction_nodes = node.xpath('./ns:Ntry', namespaces={'ns': ns})
        for entry_node in transaction_nodes:
            transaction = statement.create_transaction()
            self.parse_transaction(ns, entry_node, transaction)
        if statement['transactions']:
            statement.date = datetime.strptime(
                statement['transactions'][0].execution_date, "%Y-%m-%d")
        return statement

    def parse_transaction_details(self, ns, node, transaction):
        super(CamtParserAdv, self).parse_transaction_details(
            ns, node, transaction)
        self._parse_RltdPties(ns, node, transaction)

    def _parse_RltdPties(self, ns, node, transaction):
        """
        Handle RelatedParties <RltdPties> node
        """
        # remote party values
        party_type = 'Dbtr'
        party_type_node = node.xpath(
            '../../ns:CdtDbtInd', namespaces={'ns': ns})
        if party_type_node and party_type_node[0].text != 'CRDT':
            party_type = 'Cdtr'
        party_node = node.xpath(
            './ns:RltdPties/ns:%s' % party_type, namespaces={'ns': ns})
        if party_node:
            party_name_node = party_node[0].xpath(
                './ns:Nm', namespaces={'ns': ns})
            if party_name_node:
                party_name = party_name_node[0].text
                transaction.note += _('Partner Name') + ': %s\n' % party_name

            # WIP - Address fields

            # Get remote_account from iban or from domestic account:
            account_node = node.xpath(
                './ns:RltdPties/ns:%sAcct/ns:Id' % party_type,
                namespaces={'ns': ns}
            )
            if account_node:
                counterparty_number = counterparty_bic = ''
                iban_node = account_node[0].xpath(
                    './ns:IBAN', namespaces={'ns': ns})
                if iban_node:
                    counterparty_number = iban_node[0].text
                    bic_node = node.xpath(
                        './ns:RltdAgts/ns:%sAgt/ns:FinInstnId/ns:BIC'
                        % party_type,
                        namespaces={'ns': ns}
                    )
                    if bic_node:
                        counterparty_bic = bic_node[0].text
                else:
                    acc_nbr_node = account_node[0].xpath(
                        './ns:Othr/ns:Id')
                    if acc_nbr_node:
                        counterparty_number = acc_nbr_node[0].text
                if counterparty_bic:
                    transaction.note += _(
                        'Partner Account BIC') + ': %s\n' % counterparty_bic
                if counterparty_number:
                    transaction.note += _(
                        'Partner Account Number') + ': %s\n' % counterparty_number
