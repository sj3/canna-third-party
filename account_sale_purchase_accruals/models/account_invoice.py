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


class AccountInvoice(models.Model, CommonAccrual):
    _inherit = 'account.invoice'

    accrual_move_id = fields.Many2one(
        'account.move', string='Accrual Journal Entry',
        readonly=True, index=True, ondelete='set null', copy=False,
        help="Link to the automatically generated Accrual Entry.")
    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order', compute='_compute_purchase_order_ids',
        string="Purchase Orders")

    @api.one
    def _compute_purchase_order_ids(self):
        dom = [('invoice_ids', '=', self.id)]
        self.purchase_order_ids = self.env['purchase.order'].search(dom)

    def _create_expense_accruals(self):

        aml_vals = []
        partner = self.partner_id.commercial_partner_id

        for ail in self.invoice_line:
            product = ail.product_id
            if product:
                accrual_account = product.accrued_expense_account_id
                if not accrual_account:
                    accrual_account = product.product_tmpl_id.\
                        get_accrued_expense_account()
                if accrual_account:

                    expense_account = product.property_account_expense
                    if not expense_account:
                        expense_account = product.categ_id.\
                            property_account_expense_categ
                    if not expense_account:
                        raise UserError(
                            _("No 'Expense Account' defined for "
                              "product '%s' or the product category")
                            % product.name)
                    fpos = partner.property_account_position
                    if fpos:
                        expense_account = fpos.map_account(expense_account)
                    amount = ail.quantity * product.standard_price

                    expense_vals = {
                        'account_id': expense_account.id,
                        'debit': amount > 0 and amount or 0.0,
                        'credit': amount < 0 and -amount or 0.0,
                        'product_id': product.id,
                        'quantity': ail.quantity,
                        'partner_id': partner.id,
                        'name': ail.name,
                        'analytic_account_id': ail.account_analytic_id.id,
                        'entry_type': 'expense',
                        }
                    aml_vals.append(expense_vals)

                    accrual_vals = {
                        'account_id': accrual_account.id,
                        'debit': expense_vals['credit'],
                        'credit': expense_vals['debit'],
                        'product_id': product.id,
                        'quantity': ail.quantity,
                        'partner_id': partner.id,
                        'name': ail.name,
                        'entry_type': 'accrual',
                        }
                    aml_vals.append(accrual_vals)

            if aml_vals:
                am_id, accruals = self._create_accrual_move(aml_vals)
                self.write({'accrual_move_id': am_id})

    def _reconcile_accruals(self):
        amls = self.move_id.line_id
        for aml in amls:
            to_reconcile = aml
            product = aml.product_id
            if product:

                accrual_account = product.accrued_expense_account_id
                if not accrual_account:
                    accrual_account = product.product_tmpl_id.\
                        get_accrued_expense_account()

                if accrual_account:
                    if self.type == 'in_invoice':
                        p_accruals = [p.p_accrual_move_id
                                      for p in self.purchase_order_ids]
                        p_amls = self.env['account.move.line']
                        for p_accrual in p_accruals:
                            p_amls += p_accrual.line_id
                        for p_aml in p_amls:
                            if p_aml.account_id == accrual_account:
                                to_reconcile += p_aml

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
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self:
            if inv.type == 'out_invoice':
                inv._create_expense_accruals()
            elif inv.type == 'out_refund':
                _logger.error("WIP")
            elif inv.type == 'in_invoice':
                self._reconcile_accruals()
            elif inv.type == 'in_refund':
                _logger.error("WIP")
        return res

    @api.multi
    def action_cancel(self):
        for inv in self:
            if inv.accrual_move_id:
                inv.accrual_move_id.button_cancel()
                inv.accrual_move_id.unlink()
        return super(AccountInvoice, self).action_cancel()


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.multi
    def product_id_change(self, product_id, uom_id, qty=0, name='',
                          type='out_invoice', partner_id=False,
                          fposition_id=False, price_unit=False,
                          currency_id=False, company_id=None):
        res = super(AccountInvoiceLine, self).product_id_change(
            product_id, uom_id, qty=qty, name=name, type=type,
            partner_id=partner_id, fposition_id=fposition_id,
            price_unit=price_unit, currency_id=currency_id,
            company_id=company_id)
        if product_id:
            product = self.env['product.product'].browse(product_id)
            accrual_account = product.accrued_expense_account_id
            if not accrual_account:
                accrual_account = product.product_tmpl_id.\
                    get_accrued_expense_account()
            if accrual_account:
                res['value']['account_id'] = accrual_account
        return res
