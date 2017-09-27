# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    journal_id = fields.Many2one(required=True)
    accounting_date = fields.Date()
    period_id = fields.Many2one(
        comodel_name='account.period',
        domain=[('special', '=', False), ('state', '=', 'draft')],
        string='Period')

    @api.multi
    def onchange_currency_id(self, currency_id=False, company_id=False):
        res = super(HrExpenseExpense, self).onchange_currency_id(
            currency_id=currency_id, company_id=currency_id)
        exp = self.env['account.journal'].search(
            [('hr_expense', '=', True)])
        if exp:
            res['value']['journal_id'] = exp[0].id
        return res

    @api.model
    def account_move_get(self, expense_id):
        move_vals = super(HrExpenseExpense, self).account_move_get(expense_id)
        declaration = self.browse(expense_id)
        if declaration.accounting_date:
            move_vals['date'] = declaration.accounting_date
        if declaration.period_id:
            move_vals['period_id'] = declaration.period_id.id
        return move_vals

    @api.multi
    def generate_accounting_entries(self):
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref(
            '%s.hr_expense_expense_accounting_wizard_view_form' % module)
        return {
            'name': _("Generate Accounting Entries"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.expense.expense.accounting.wizard',
            'view_id': view.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': self._context,
        }


class HrExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    line_state = fields.Selection(
        related='expense_id.state')

    @api.multi
    def update_product(self):
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref(
            '%s.hr_expense_line_product_wizard_view_form' % module)
        return {
            'name': _("Update Product"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.expense.line.product.wizard',
            'view_id': view.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': self._context,
        }