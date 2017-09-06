# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def unlink(self, **kwargs):
        for move in self:
            exp = self.env['hr.expense.expense'].search(
                [('account_move_id', '=', move.id)])
            if exp:
                raise UserError(
                    _('Error!'),
                    _("You are not allowed to remove an accounting entry "
                      "linked to an HR Expense."))
        return super(AccountMove, self).unlink(**kwargs)

    @ api.multi
    def post(self):
        if 'fiscalyear_id' not in self._context:
            ctx = self._context.copy()
            for am in self:
                if not am.name or am.name == '/':
                    ctx['fiscalyear_id'] = am.period_id.fiscalyear_id.id
                super(AccountMove, am.with_context(ctx)).post()
            return True
        else:
            return super(AccountMove, self).post()
