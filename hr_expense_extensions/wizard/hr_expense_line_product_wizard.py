# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class HrExpenseLineProductWizard(models.TransientModel):
    _name = 'hr.expense.line.product.wizard'

    product_id = fields.Many2one(
        comodel_name='product.product',
        domain=[('hr_expense_ok', '=', True)],
        string='Product', required=True)

    @api.multi
    def update(self):
        line = self.env['hr.expense.line'].browse(
            self._context.get('active_id'))
        line.product_id = self.product_id
