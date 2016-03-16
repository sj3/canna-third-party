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

from openerp import api, fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    accrued_expense_in_account_id = fields.Many2one(
        'account.account', string='Accrued Expense In Account',
        domain=[('type', 'not in', ['view', 'closed', 'consolidation'])],
        company_dependent=True, ondelete='restrict',
        help="Set this account to create an accrual for the cost of goods "
             "or services during the procurement operation.")
    accrued_expense_out_account_id = fields.Many2one(
        'account.account', string='Accrued Expense Out Account',
        domain=[('type', 'not in', ['view', 'closed', 'consolidation'])],
        company_dependent=True, ondelete='restrict',
        help="Set this account to create an accrual for the cost of goods "
             "or services during the sales operation.")
    supply_method = fields.Selection(
        selection=lambda self: self._supply_method_select(),
        string='Supply Method', company_dependent=True,
        help="Set this parameter in order to enforce the selected "
             "supply Method for the products in this category.")

    @api.one
    def _supply_method_select(self):
        # TODO: create module to add ('manufacture', 'Manufacture')
        return [
            ('stock', 'Take From Stock'),
            ('buy', 'Buy')]

    @api.multi
    def get_accrued_expense_in_account(self):
        self.ensure_one()
        if self.accrued_expense_in_account_id:
            res = self.accrued_expense_in_account_id
        elif self.parent_id:
            res = self.parent_id.get_accrued_expense_in_account()
        else:
            res = self.env['account.account']
        return res

    @api.multi
    def get_accrued_expense_out_account(self):
        self.ensure_one()
        if self.accrued_expense_out_account_id:
            res = self.accrued_expense_out_account_id
        elif self.parent_id:
            res = self.parent_id.get_accrued_expense_out_account()
        else:
            res = self.env['account.account']
        return res

    @api.multi
    def get_supply_method(self):
        self.ensure_one()
        if self.supply_method:
            res = self.supply_method
        elif self.parent_id:
            res = self.parent_id.get_supply_method()
        else:
            res = False
        return res
