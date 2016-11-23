# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    note = fields.Text(string='Log')

    @api.multi
    def import_file(self):
        """
        Replacement of import method in order to disable the
        automatic dispatch of the reconciliation interface.

        Such a dispatch must take place after running
        auto-reconcile/posting logic in order to filter out
        the entries which do not require manual intervention.
        """
        self.ensure_one()
        data_file = base64.b64decode(self.data_file)
        # pylint: disable=protected-access
        statement_ids, notifications = self.with_context(
            active_id=self.id  # pylint: disable=no-member
        )._import_file(data_file)

        self.note = ''
        for notification in notifications:
            self.note += notification['type'] + ':\n'
            self.note += notification['message'] + '\n'
            self.note += notification['details'] + '\n\n'
        self.note += _("Number of statements processed") \
            + ' : ' + str(len(statement_ids))

        ctx = self._context.copy()
        ctx.update({
            'bk_st_ids': statement_ids,
            })
        module = __name__.split('addons.')[1].split('.')[0]
        result_view = self.env.ref(
            '%s.account_bank_statement_import_view_form_result' % module)

        return {
            'name': _('Import Bank Statement File result'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.bank.statement.import',
            'view_id': result_view.id,
            'target': 'new',
            'context': ctx,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def action_open_bank_statements(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id(
            'account', 'action_bank_statement_tree')
        domain = [('id', 'in', self._context.get('bk_st_ids'))]
        action.update({'domain': domain})
        return action
