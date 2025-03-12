# -*- coding: utf-8 -*-

from odoo import models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def copy(self, default=None):
        if self._context.get('account_invoice_split'):
            default = {} if default is None else default.copy()
            default['line_ids'] = []
        return super(AccountMove, self).copy(default=default)

    def split_invoice(self):
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_(
                "Only draft invoices can be splitted"))
        if len(self.invoice_line_ids) < 2:
            raise UserError(_(
                "At least two invoice lines required for a split"))
        module = __name__.split('addons.')[1].split('.')[0]
        view = self.env.ref(f"{module}.account_move_split_view_form")
        ctx = self._context.copy()
        ctx['default_invoice_split_line_ids'] = self.invoice_line_ids.ids
        return {
            'name': _('Select Invoice Lines'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move.split',
            'type': 'ir.actions.act_window',
            'view': view.id,
            'target': 'new',
            'context': ctx,
            }
