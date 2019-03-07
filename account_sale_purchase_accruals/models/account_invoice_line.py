# -*- coding: utf-8 -*-
# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models, _
from openerp.exceptions import Warning as UserError


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    sale_order_line_ids = fields.Many2many(
        comodel_name='sale.order.line',
        relation='sale_order_line_invoice_rel',
        column1='invoice_id',
        column2='order_line_id',
        string='Sale Order Lines')

    def _get_procurement_action(self):
        action = False
        product = self.product_id
        if product.type in ('product', 'consu'):
            if self.invoice_id.type == 'out_refund' and self.origin_line_ids:
                if len(self.origin_line_ids) > 1:
                    module = __name__.split('addons.')[1].split('.')[0]
                    raise UserError(_(
                        "Programming Error detected in %s"
                        "Please report this error via your Odoo "
                        "support channel."
                    ) % ', '.join([module, self._name]))
                proc_inv_line = self.origin_line_ids
            else:
                proc_inv_line = self
            dom = [
                ('invoice_lines', '=', proc_inv_line.id),
                ('product_id', '=', product.id)]
            sols = self.env['sale.order.line'].search(dom)
            procs = sols.mapped('procurement_ids')
            rules = procs.mapped('rule_id')
            actions = rules.mapped('action')
            if len(actions) == 1:
                action = actions[0]
        return action
