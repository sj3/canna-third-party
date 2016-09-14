# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2015 Onestein BV (www.onestein.eu).
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

from openerp import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    purchase_order_ids = fields.Many2many(
        comodel_name='purchase.order',
        compute='_compute_purchase_order_ids',
        search='_search_purchase_order_ids',
        string='Purchase Orders',
    )
    purchase_order_count = fields.Integer(
        compute='_compute_purchase_order_ids',
        string='# of Sales Order'
    ) 
    @api.one
    def _compute_purchase_order_ids(self):
        procs = self.env['procurement.order'].search(
            [('sale_order_id', '=', self.id),
             ('state', '!=', 'cancel')
             ])
        self.purchase_order_ids = procs.mapped('purchase_id')
        self.purchase_order_count = len(self.purchase_order_ids)

    @api.model
    def _search_purchase_order_ids(self, operator, value):
        if operator == 'in':
            if isinstance(value, int):
                value = [value]
            so_ids = self.env['procurement.order'].search(
                [('purchase_id', 'in', value),
                 ('state', '!=', 'cancel')
             ]).mapped('sale_order_id.id')
            return [('id', 'in', so_ids)]
        else:
            raise UserError(_('Unsupported operand for search!'))

    @api.multi
    def view_purchase_order(self):
        self.ensure_one()
        action = {}
        po_ids = [x.id for x in self.purchase_order_ids]
        if po_ids:
            form = self.env.ref(
                    'purchase.purchase_order_form')
            if len(po_ids) > 1:
                tree = self.env.ref(
                    'purchase.purchase_order_tree')
                action.update({
                    'name': _('Purchase Orders'),
                    'view_mode': 'tree,form',
                    'views': [(tree.id, 'tree'), (form.id, 'form')],
                    'domain': [('id', 'in', po_ids)],
                    })
            else:
                action.update({
                    'name': _('Purchase Order'),
                    'view_mode': 'form',
                    'view_id': form.id,
                    'res_id': po_ids[0],
                    })
            action.update({
                'context': self._context,
                'view_type': 'form',
                'res_model': 'purchase.order',
                'type': 'ir.actions.act_window',
                })
        return action
