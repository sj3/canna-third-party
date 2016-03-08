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

import logging

from openerp import api, fields, models, _
from openerp.addons.account_sale_purchase_accruals.models.common_accrual \
    import CommonAccrual
from openerp.exceptions import Warning as UserError

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
    sale_order_ids = fields.Many2many(
        comodel_name='sale.order', compute='_compute_sale_order_ids',
        string="Sale Orders")

    @api.one
    def _compute_purchase_order_ids(self):
        dom = [('invoice_ids', '=', self.id)]
        self.purchase_order_ids = self.env['purchase.order'].search(dom)

    @api.one
    def _compute_sale_order_ids(self):
        dom = [('invoice_ids', '=', self.id)]
        self.sale_order_ids = self.env['sale.order'].search(dom)

    def _customer_invoice_create_expense_accruals(self):
        """
        - Create 'Accrued Expense Account' entries for the Customer Invoice.
        - Reconcile these 'Accrued Expense Account' entries
          with it's counterpart created during the Procurement Process
          (e.g. Purchase Order Confirmation).
        """
        aml_vals = []
        inv_accruals = {}
        inv_accrual_accounts = []
        partner = self.partner_id.commercial_partner_id

        for ail in self.invoice_line:
            product = ail.product_id
            if product:
                accrual_account = product.recursive_accrued_expense_account_id
                if accrual_account:

                    inv_accrual_accounts.append(accrual_account)
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
                    if self.type == 'out_refund':
                        amount = -amount

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
            am_id, inv_accruals = self._create_accrual_move(aml_vals)
            self.write({'accrual_move_id': am_id})

        dom = [('sale_order_ids', 'in', self.sale_order_ids)]
        purchase_orders = self.env['purchase.order'].search(dom)
        po_accruals = purchase_orders.mapped('s_accrual_move_id')
        for po_accrual in po_accruals:
            for l in po_accrual.line_id:
                if l.product_id.id in inv_accruals \
                        and l.account_id in inv_accrual_accounts:
                    inv_accruals[l.product_id.id] += l

        # TODO: extend logic for stock & manufacturing procurements
        if po_accruals:
            self._reconcile_accrued_expense_lines(inv_accruals)

        # reconcile refund accrual with original invoice accrual
        # remark: this operation may fail, e.g. if original invoice
        # accrual is already reconciled during procurement proces.
        accrual_lines = {}
        for aml in self.accrual_move_id.line_id:
            if aml.account_id in inv_accrual_accounts:
                accrual_lines[aml.product_id.id] = aml
        # Logic infra doesn't cover refund validated via refund wizard
        # since origin_invoices_ids field is populated after the validation.
        # As a consequence we have added the same logic to the refund wizard.
        for origin_invoice in self.origin_invoices_ids:
            for orig_aml in origin_invoice.accrual_move_id.line_id:
                if orig_aml.account_id in inv_accrual_accounts \
                        and not orig_aml.reconcile_id:
                    if orig_aml.product_id.id in accrual_lines:
                        accrual_lines[orig_aml.product_id.id] += orig_aml
        if accrual_lines:
            self._reconcile_accrued_expense_lines(accrual_lines)

    def _supplier_invoice_reconcile_accruals(self):
        """
        Reconcile the 'Accrued Expense Account' entries of the
        Purchase Invoice with it's counterpart created during the
        Purchase Order Confirmation.
        """
        amls = self.move_id.line_id
        accrual_lines = {}
        for aml in amls:
            product = aml.product_id
            accrual_lines[product.id] = aml
            if product:
                accrual_account = product.recursive_accrued_expense_account_id
                if accrual_account:
                    accruals = [po.p_accrual_move_id
                                for po in self.purchase_order_ids]
                    amls = self.env['account.move.line']
                    for accrual in accruals:
                        amls += accrual.line_id
                    for aml in amls:
                        if aml.account_id == accrual_account:
                            accrual_lines[product.id] += aml
        if accrual_lines:
            self._reconcile_accrued_expense_lines(accrual_lines)

    @api.multi
    def invoice_validate(self):
        res = super(AccountInvoice, self).invoice_validate()
        for inv in self:
            if inv.type in ('out_invoice', 'out_refund'):
                inv._customer_invoice_create_expense_accruals()
            elif inv.type == 'in_invoice':
                inv._supplier_invoice_reconcile_accruals()
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
        if type in ('in_invoice', 'in_refund') and product_id:
            product = self.env['product.product'].browse(product_id)
            accrual_account = product.recursive_accrued_expense_account_id
            if accrual_account:
                res['value']['account_id'] = accrual_account
        return res
