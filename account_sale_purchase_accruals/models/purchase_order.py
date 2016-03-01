# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from openerp.addons.account_sale_purchase_accruals.models.common_accrual \
    import CommonAccrual
from openerp.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model, CommonAccrual):
    _inherit = 'purchase.order'

    s_accrual_move_id = fields.Many2one(
        'account.move', string='Sales Invoice Counterpart Accrual',
        readonly=True, index=True, ondelete='set null', copy=False,
        help="Link to the Accrual Entry which is the counterparty "
             " of the Sales Invoice Accrual Entry.")
    p_accrual_move_id = fields.Many2one(
        'account.move', string='Purchase Invoice Counterpart Accrual',
        readonly=True, index=True, ondelete='set null', copy=False,
        help="Link to the 'Invoice to Receive' Accrual Entry.")

    @api.model
    def _prepare_invoice(self, po, line_ids):
        """
        Use the Journal selected on the PO
        """
        inv_vals = super(PurchaseOrder, self)._prepare_invoice(po, line_ids)
        inv_vals['journal_id'] = po.journal_id.id
        return inv_vals

    @api.model
    def _prepare_inv_line(self, account_id, order_line):
        vals = super(PurchaseOrder, self)._prepare_inv_line(
            account_id, order_line)
        product_id = vals.get('product_id')
        if product_id:
            product = self.env['product.product'].browse(product_id)
            accrual_account = product.accrued_expense_account_id
            if not accrual_account:
                accrual_account = product.product_tmpl_id.\
                    get_accrued_expense_account()
            if accrual_account:
                vals['account_id'] = accrual_account.id
        return vals

    def _prepare_accrual_move_ref(self):
        sale_orders = self.sale_order_ids or []
        return ', '.join(
            [x.name for x in sale_orders] + [self.name])

    def _create_accrual_moves(self):
        """
        Create accrued expense entries + reconcile
        with counterparts created at Sales Invoice validation.

        The cost which has been nullified by this operation
        is reintroduced via a new accrual which now takes care of
        company currency and foreign currency.
        """
        partner = self.partner_id.commercial_partner_id
        fpos = partner.property_account_position
        cur = self.with_context(date=self.date_order).currency_id
        cpy_cur = self.company_id.currency_id
        s_aml_vals = []
        s_po_accruals = {}
        po_accrual_accounts = []
        p_aml_vals = []

        for pol in self.order_line:
            product = pol.product_id
            if product:
                accrual_account = product.accrued_expense_account_id
                if not accrual_account:
                    accrual_account = product.product_tmpl_id.\
                        get_accrued_expense_account()
                if accrual_account:

                    po_accrual_accounts.append(accrual_account)
                    expense_account = product.property_account_expense
                    if not expense_account:
                        expense_account = product.categ_id.\
                            property_account_expense_categ
                    if not expense_account:
                        raise UserError(
                            _("No 'Expense Account' defined for "
                              "product '%s' or the product category")
                            % product.name)

                    if fpos:
                        expense_account = fpos.map_account(expense_account)
                    amount = pol.product_qty * product.standard_price
                    if not amount:
                        raise UserError(
                            _("No 'Cost' defined for product '%s'")
                            % product.name)
                    debit = amount < 0 and -amount or 0.0
                    credit = amount > 0 and amount or 0.0

                    # prepare s_accrual_move

                    expense_vals = {
                        'account_id': expense_account.id,
                        'debit': debit,
                        'credit': credit,
                        'product_id': product.id,
                        'quantity': pol.product_qty,
                        'partner_id': partner.id,
                        'name': pol.name,
                        'analytic_account_id': pol.account_analytic_id.id,
                        'entry_type': 'expense',
                        }
                    s_aml_vals.append(expense_vals)

                    accrual_vals = {
                        'account_id': accrual_account.id,
                        'debit': credit,
                        'credit': debit,
                        'product_id': product.id,
                        'quantity': pol.product_qty,
                        'partner_id': partner.id,
                        'name': pol.name,
                        'entry_type': 'accrual',
                        }
                    s_aml_vals.append(accrual_vals)

                    # prepare p_accrual_move

                    amount = pol.price_subtotal
                    if not amount:
                        raise UserError(
                            _("No price defined for order line '%s'")
                            % pol.name)
                    if cur != cpy_cur:
                        amt_cpy_cur = cur.compute(amount, cpy_cur)
                    else:
                        amt_cpy_cur = amount
                    debit = amount > 0 and amt_cpy_cur or 0.0
                    credit = amount < 0 and -amt_cpy_cur or 0.0

                    expense_vals = {
                        'account_id': expense_account.id,
                        'debit': debit,
                        'credit': credit,
                        'product_id': product.id,
                        'quantity': pol.product_qty,
                        'partner_id': partner.id,
                        'name': pol.name,
                        'analytic_account_id': pol.account_analytic_id.id,
                        'entry_type': 'expense',
                        }
                    if cur != cpy_cur:
                        expense_vals.update({
                            'currency_id': cur.id,
                            'amount_currency': amount,
                            })
                    p_aml_vals.append(expense_vals)

                    accrual_vals = {
                        'account_id': accrual_account.id,
                        'debit': credit,
                        'credit': debit,
                        'product_id': product.id,
                        'quantity': pol.product_qty,
                        'partner_id': partner.id,
                        'name': pol.name,
                        'entry_type': 'accrual',
                        }
                    if cur != cpy_cur:
                        accrual_vals.update({
                            'currency_id': cur.id,
                            'amount_currency': -amount,
                            })
                    p_aml_vals.append(accrual_vals)

            if s_aml_vals:
                am_id, s_po_accruals = self._create_accrual_move(s_aml_vals)
                self.write({'s_accrual_move_id': am_id})
                am_id, p_po_accruals = self._create_accrual_move(p_aml_vals)
                self.write({'p_accrual_move_id': am_id})

        for so in self.sale_order_ids:
            for inv in so.invoice_ids:
                for l in inv.accrual_move_id.line_id:
                    if l.product_id.id in s_po_accruals \
                            and l.account_id in po_accrual_accounts:
                        s_po_accruals[l.product_id.id] += l

        for p_id in s_po_accruals:
            to_reconcile = s_po_accruals[p_id]
            check = 0.0
            for l in to_reconcile:
                check += l.debit - l.credit
            if self.company_id.currency_id.is_zero(check):
                to_reconcile.reconcile()
            else:
                _logger.error(_(
                    "%s, accrual reconcile failed for "
                    "account.move.line ids %s, "
                    "sum(debit) != sum(credit)"),
                    self.name, [x.id for x in to_reconcile]
                    )

    @api.multi
    def wkf_confirm_order(self):
        super(PurchaseOrder, self).wkf_confirm_order()
        for po in self:
            po._create_accrual_moves()
        return True

    @api.multi
    def wkf_action_cancel(self):
        for po in self:
            for accrual in [po.s_accrual_move_id, po.p_accrual_move_id]:
                if accrual:
                    accrual.button_cancel()
                    accrual.unlink()
        return super(PurchaseOrder, self).action_cancel()