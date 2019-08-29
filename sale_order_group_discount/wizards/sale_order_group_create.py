# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _


class SaleOrderGroupCreate(models.TransientModel):
    _inherit = 'sale.order.group.create'

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrderGroupCreate, self).default_get(fields_list)
        orders = self.env['sale.order'].browse(
            self.env.context.get('active_ids'))
        discounts = orders[0].discount_ids
        for order in orders[1:]:
            if order.discount_ids != discounts:
                msg = '\n\n' + _("Warning:") + '\n'
                msg += _(
                    "The selected orders have different discounts. "
                    "Align these discounts first if you want to apply "
                    "the discount calculation on the combined set of orders."
                )
                res['note'] += msg
                break
        return res

    def _prepare_sale_order_group_vals(self):
        """
        Add discounts to vals only if all grouped orders have the
        same discounts.
        """
        vals = super(
            SaleOrderGroupCreate, self)._prepare_sale_order_group_vals()
        orders = self.env['sale.order'].browse(
            self.env.context.get('active_ids'))
        discounts = orders[0].discount_ids
        for order in orders[1:]:
            if order.discount_ids != discounts:
                return vals
        vals['discount_ids'] = [(6, 0, discounts.ids)]
        return vals
