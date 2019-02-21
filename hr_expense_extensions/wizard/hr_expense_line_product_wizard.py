# -*- coding: utf-8 -*-
# Copyright 2009-2019 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class HrExpenseLineProductWizard(models.TransientModel):
    _name = 'hr.expense.line.product.wizard'

    product_id = fields.Many2one(
        comodel_name='product.product',
        domain=[('hr_expense_ok', '=', True)],
        string='Product', required=True,
        default=lambda self: self._default_product_id())

    exp_line = fields.Many2one(
        comodel_name='hr.expense.line',
        string='HR Expense Line',
        default=lambda self: self._default_exp_line())

    @api.model
    def _default_exp_line(self):
        return self.env['hr.expense.line'].browse(
            self._context.get('active_id'))

    @api.model
    def _default_product_id(self):
        return self._default_exp_line().product_id.id

    @api.multi
    def update(self):
        self.exp_line.product_id = self.product_id
