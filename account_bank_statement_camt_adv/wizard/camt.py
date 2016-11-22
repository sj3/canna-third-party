# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from openerp.addons.account_bank_statement_import_camt.camt \
    import CamtParser as Parser
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
        _logger.error('parse_transaction_details, transaction=%s',
                      transaction)
        """
        # message
        self.add_value_from_node(
            ns, node, [
                './ns:RmtInf/ns:Ustrd',
                './ns:AddtlTxInf',
                './ns:AddtlNtryInf',
            ], transaction, 'message', join_str='\n')
        # eref
        self.add_value_from_node(
            ns, node, [
                './ns:RmtInf/ns:Strd/ns:CdtrRefInf/ns:Ref',
                './ns:Refs/ns:EndToEndId',
            ],
            transaction, 'eref'
        )
        # remote party values
        party_type = 'Dbtr'
        party_type_node = node.xpath(
            '../../ns:CdtDbtInd', namespaces={'ns': ns})
        if party_type_node and party_type_node[0].text != 'CRDT':
            party_type = 'Cdtr'
        party_node = node.xpath(
            './ns:RltdPties/ns:%s' % party_type, namespaces={'ns': ns})
        if party_node:
            self.add_value_from_node(
                ns, party_node[0], './ns:Nm', transaction, 'remote_owner')
            self.add_value_from_node(
                ns, party_node[0], './ns:PstlAdr/ns:Ctry', transaction,
                'remote_owner_country'
            )
            address_node = party_node[0].xpath(
                './ns:PstlAdr/ns:AdrLine', namespaces={'ns': ns})
            if address_node:
                transaction.remote_owner_address = [address_node[0].text]
        # Get remote_account from iban or from domestic account:
        account_node = node.xpath(
            './ns:RltdPties/ns:%sAcct/ns:Id' % party_type,
            namespaces={'ns': ns}
        )
        if account_node:
            iban_node = account_node[0].xpath(
                './ns:IBAN', namespaces={'ns': ns})
            if iban_node:
                transaction.remote_account = iban_node[0].text
                bic_node = node.xpath(
                    './ns:RltdAgts/ns:%sAgt/ns:FinInstnId/ns:BIC' % party_type,
                    namespaces={'ns': ns}
                )
                if bic_node:
                    transaction.remote_bank_bic = bic_node[0].text
            else:
                self.add_value_from_node(
                    ns, account_node[0], './ns:Othr/ns:Id', transaction,
                    'remote_account'
                )
        """
