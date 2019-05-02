# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
# from openerp.exceptions import Warning as UserError


class SaleOrderGroupCreate(models.TransientModel):
    _name = 'sale.order.group.create'
    _description = 'Create Sale Order Group'

    state = fields.Selection(
        selection=[('error', 'Error')],
        readonly=True)
    note = fields.Text(
        string='Notes')

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderGroupCreate, self).default_get(fields_list)
        error = ''
        state = False
        orders = self.env['sale.order'].browse(
            self.env.context.get('active_ids'))
        if len(orders) == 1:
            error += '\n' + _(
                "A minimum of 2 orders must be selected."
            )
            state = 'error'
        commercial_partner = self.env['res.partner']
        for order in orders:
            if order.state not in ['draft', 'sent']:
                error += '\n' + _(
                    "Only draft orders can be selected. "
                    "Please deselect order '%s'."
                ) % order.name
                state = 'error'
            if order.sale_order_group_id:
                error += '\n' + _(
                    "Order '%s' already belongs to a Sale Order Group."
                ) % order.name
                state = 'error'
            commercial_partner |= order.partner_id.commercial_partner_id
        if len(commercial_partner) > 1:
            error += '\n' + _(
                "All selected orders must belong to the same partner.")
            state = 'error'
        if state == 'error':
            note = _("The selected orders can not be grouped together.")
            note += '\n\n' + _('Reason') + ':\n' + error
        else:
            note = _(
                "The following orders for Partner '%s' "
                "will be grouped together:"
            ) % commercial_partner.name + '\n\n'
            note += ', '.join([str(x) for x in orders.mapped('name')])
        res.update({
            'note': note,
            'state': state,
        })
        return res

    @api.multi
    def group_orders(self):
        orders = self.env['sale.order'].browse(
            self.env.context.get('active_ids'))
        partner = orders[0].partner_id.commercial_partner_id
        vals = {
            'state': 'draft',
            'sale_order_ids': [(6, 0, orders.ids)],
            'partner_id': partner.id,
        }
        self.env['sale.order.group'].create(vals)
        return {'type': 'ir.actions.act_window_close'}
