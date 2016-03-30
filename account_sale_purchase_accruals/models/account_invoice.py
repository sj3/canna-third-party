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
        - Create Accrual entries for the Customer Invoice.
        - Reconcile these entries with it's counterpart created during the
          Procurement Process in case of dropshipping
          (Purchase Order Confirmation) or
          the Outgoing Shipment in case of delivery from stock(.
        """
        aml_vals = []
        inv_accruals = {}
        inv_accrual_accounts = []
        partner = self.partner_id.commercial_partner_id
        supply_partner = partner

        # find associated pickings or purchase orders
        so_dom = [('sale_order_id', 'in', self.sale_order_ids._ids)]
        procs = self.env['procurement.order'].search(so_dom)
        proc_groups = procs.mapped('group_id')
        sp_dom = [('group_id', 'in', proc_groups._ids)]
        stock_pickings = self.env['stock.picking'].search(sp_dom)
        if not stock_pickings:
            purchase_orders = procs.mapped('purchase_id')
        else:
            purchase_orders = self.env['purchase.order']

        for ail in self.invoice_line:
            product = ail.product_id

            if not product:
                continue

            procurement_action = ail._get_procurement_action()
            if procurement_action == 'move':
                if product.valuation == 'real_time':
                    accrual_account = \
                        product.recursive_property_stock_account_output
                else:
                    continue
            elif procurement_action == 'buy':
                accrual_account = \
                    product.recursive_accrued_expense_out_account_id
            else:
                continue

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
                if not amount:
                    raise UserError(
                        _("No 'Cost' defined for product '%s'")
                        % product.name)

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
                    'partner_id': procurement_action == 'move' \
                        and partner.id or False,
                    'name': ail.name,
                    'entry_type': 'accrual',
                    }
                aml_vals.append(accrual_vals)

        if aml_vals:
            am_id, inv_accruals = self._create_accrual_move(aml_vals)
            self.write({'accrual_move_id': am_id})

        # reconcile with Stock Valuation or PO accruals
        if stock_pickings:
            accruals = stock_pickings.mapped('valuation_move_ids')
        else:
            accruals = purchase_orders.mapped('s_accrual_move_id')
        if accruals:
            amls = accruals.mapped('line_id')
            for aml in amls:
                if aml.product_id.id in inv_accruals \
                        and aml.account_id in inv_accrual_accounts:
                    inv_accruals[aml.product_id.id] += aml
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
        Reconcile the accruel entries of the
        Purchase Invoice with it's counterpart created during the
        Purchase Order Confirmation or Incoming Picking.
        """
        si_amls = self.move_id.line_id
        accrual_lines = {}
        for si_aml in si_amls:
            product = si_aml.product_id
            if product:
                accrual_account = \
                    product.recursive_property_stock_account_input
                if si_aml.account_id == accrual_account:
                    accrual_lines[product.id] = si_aml
                    pickings = self.purchase_order_ids.mapped('picking_ids')
                    accruals = pickings.valuation_move_ids
                else:
                    accrual_account = \
                        product.recursive_accrued_expense_in_account_id
                    if accrual_account \
                            and si_aml.account_id == accrual_account:
                        accrual_lines[product.id] = si_aml
                        accruals = self.purchase_order_ids.mapped(
                            'p_accrual_move_id')
                    else:
                        return
                amls = accruals.mapped('line_id')
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

    def _get_procurement_action(self):
        action = False
        product = self.product_id
        if product.type in ('product', 'consu'):
            dom = [
                ('invoice_lines', '=', self.id),
                ('product_id', '=', product.id)]
            sols = self.env['sale.order.line'].search(dom)
            procs = sols.mapped('procurement_ids')
            rules = procs.mapped('rule_id')
            actions = rules.mapped('action')
            if len(actions) == 1:
                action = actions[0]
        return action
