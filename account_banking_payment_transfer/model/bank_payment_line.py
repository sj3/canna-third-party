# -*- coding: utf-8 -*-
# © 2009 EduSense BV (<http://www.edusense.nl>)
# © 2011-2013 Therp BV (<http://therp.nl>)
# © 2015 Akretion (www.akretion.com)
# © 2017 Noviat (www.noviat.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import Warning as UserError


class BankPaymentLine(models.Model):
    _inherit = 'bank.payment.line'

    transit_move_line_id = fields.Many2one(
        'account.move.line', string='Transfer move line', readonly=True,
        help="Move line through which the payment/debit order "
        "pays the invoice")
    transfer_move_line_id = fields.Many2one(
        'account.move.line', compute='_get_transfer_move_line',
        string='Transfer move line counterpart',
        help="Counterpart move line on the transfer account",
        store=True)

    @api.multi
    def move_line_transfer_account_hashcode(self):
        """
        This method is inherited in the module
        account_banking_sepa_direct_debit
        """
        self.ensure_one()
        if self.order_id.mode.transfer_move_option == 'date':
            hashcode = self.date
        else:
            hashcode = unicode(self.id)
        return hashcode

    @api.multi
    @api.depends(
        'transit_move_line_id.move_id.line_id.debit',
        'transit_move_line_id.move_id.line_id.credit',
        'order_id.payment_order_type',
    )
    def _get_transfer_move_line(self):
        for bank_line in self:
            if bank_line.transit_move_line_id:
                order_type = bank_line.order_id.payment_order_type
                trf_lines = bank_line.transit_move_line_id.move_id.line_id
                for move_line in trf_lines:
                    if order_type == 'debit' and move_line.debit > 0:
                        bank_line.transfer_move_line_id = move_line
                    elif order_type == 'payment' and move_line.credit > 0:
                        bank_line.transfer_move_line_id = move_line

    @api.one
    def debit_reconcile(self):
        """
        Reconcile a debit order's payment line with the the move line
        that it is based on. Called from payment_order.action_sent().
        As the amount is derived directly from the counterpart move line,
        we do not expect a write off. Take partial reconciliations into
        account though.

        :param payment_line_id: the single id of the canceled payment line
        """

        transit_move_line = self.transit_move_line_id

        assert not transit_move_line.reconcile_id,\
            'Transit move should not be reconciled'
        assert not transit_move_line.reconcile_partial_id,\
            'Transit move should not be partially reconciled'
        lines_to_rec = transit_move_line
        for payment_line in self.payment_line_ids:

            if not payment_line.move_line_id:
                raise UserError(_(
                    "Can not reconcile: no move line for "
                    "payment line %s of partner '%s'.") % (
                        payment_line.name,
                        payment_line.partner_id.name))
            if payment_line.move_line_id.reconcile_id:
                raise UserError(_(
                    "Move line '%s' of partner '%s' has already "
                    "been reconciled") % (
                        payment_line.move_line_id.name,
                        payment_line.partner_id.name))
            if (
                    payment_line.move_line_id.account_id !=
                    transit_move_line.account_id):
                raise UserError(_(
                    "For partner '%s', the account of the account "
                    "move line to pay (%s) is different from the "
                    "account of of the transit move line (%s).") % (
                        payment_line.move_line_id.partner_id.name,
                        payment_line.move_line_id.account_id.code,
                        transit_move_line.account_id.code))

            lines_to_rec += payment_line.move_line_id

        # add currency diff when payment in foreign currency
        cur_amts = lines_to_rec.mapped('amount_currency')
        curs = lines_to_rec.mapped('currency_id')
        if any(cur_amts) and len(curs) == 1 and sum(cur_amts) == 0.0:
            debits = lines_to_rec.mapped('debit')
            credits = lines_to_rec.mapped('credit')
            diff = sum(debits) - sum(credits)
            if diff:
                aml_mod = self.env['account.move.line']
                cur_line_vals = self._get_cur_line_vals(
                    transit_move_line, diff)
                aml1 = aml_mod.create(cur_line_vals[0])
                lines_to_rec += aml1
                aml_mod.create(cur_line_vals[1])
        lines_to_rec.reconcile_partial(type='auto')

    def _get_cur_line_vals(self, transit_move_line, diff):
        move = transit_move_line.move_id
        if diff > 0:
            exch_acc = self.company_id.income_currency_exchange_account_id
        else:
            exch_acc = self.company_id.expense_currency_exchange_account_id
        vals1 = {
            'move_id': move.id,
            'name': _('currency rate difference'),
            'account_id': transit_move_line.account_id.id,
            'partner_id': transit_move_line.partner_id.id,
            'currency_id': transit_move_line.currency_id.id,
            'debit': diff < 0 and -diff or 0.0,
            'credit': diff > 0 and diff or 0.0,
        }
        vals2 = {
            'move_id': move.id,
            'name': _('currency rate difference'),
            'account_id': exch_acc.id,
            'debit': vals1['credit'],
            'credit': vals1['debit'],
        }
        return (vals1, vals2)
