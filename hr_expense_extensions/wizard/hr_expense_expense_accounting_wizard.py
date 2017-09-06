# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class HrExpenseExpenseAccountingWizard(models.TransientModel):
    _name = 'hr.expense.expense.accounting.wizard'

    date = fields.Date(
        string='Accounting Date', required=True,
        default=lambda self: self._default_date())
    period_id = fields.Many2one(
        comodel_name='account.period',
        domain=[('special', '=', False), ('state', '=', 'draft')],
        string='Period', required=True,
        default=lambda self: self._default_period_id())

    @api.model
    def _default_date(self):
        declaration = self.env['hr.expense.expense'].browse(
            self._context['active_id'])
        return declaration.date

    @api.model
    def _default_period_id(self):
        declaration = self.env['hr.expense.expense'].browse(
            self._context['active_id'])
        period = self.env['account.period'].find(dt=declaration.date)
        return period

    @api.multi
    def generate(self):
        declaration = self.env['hr.expense.expense'].browse(
            self._context['active_id'])
        declaration.accounting_date = self.date
        declaration.period_id = self.period_id
        declaration.signal_workflow('done')
