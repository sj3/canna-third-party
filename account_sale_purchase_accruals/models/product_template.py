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


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    accrued_expense_account_id = fields.Many2one(
        'account.account', string='Accrued Expense Account',
        domain=[('type', 'not in', ['view', 'closed', 'consolidation'])],
        company_dependent=True, ondelete='restrict',
        help="Set this account to create an accrual for the cost of goods "
             "or services when confirming the Sales Order.")
    recursive_accrued_expense_account_id = fields.Many2one(
        'account.account', string='Accrued Expense Account',
        compute='_compute_recursive_accrued_expense_account_id',
        company_dependent=True,
        help="Accrued Expense Account on Product Record or Product Category.")

    @api.multi
    def _compute_recursive_accrued_expense_account_id(self):
        if self.accrued_expense_account_id:
            account = self.accrued_expense_account_id
        elif self.categ_id:
            account = self.categ_id.get_accrued_expense_account()
        else:
            account = self.env['account.account']
        self.recursive_accrued_expense_account_id = account

    @api.multi
    def get_accrued_expense_account(self):
        self.ensure_one()
        if self.accrued_expense_account_id:
            res = self.accrued_expense_account_id
        elif self.categ_id:
            res = self.categ_id.get_accrued_expense_account()
        else:
            res = self.env['account.account']
        return res
