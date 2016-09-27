# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_discount_line = fields.Boolean(
        string="Line is a sale discount line",
        help="This field is used to manage the lines "
        "made by the sale discount module."
    )

    sale_discounts = fields.Many2many(
        comodel_name='sale.discount',
        relation='sale_line_sale_discount_rel',
        column1='sale_line_id',
        column2='discount_id',
        string="Discount(s)"
    )

    @api.one
    @api.onchange('price_unit', 'product_uom_qty', 'product_id')
    def _onchange_discount(self):
        if self.sale_discount_line or not self.product_id:
            return

        for discount in self.order_id._get_active_discounts():
            if discount in self.sale_discounts:
                continue

            if self.product_id in discount.product_ids:
                self.sale_discounts += discount
            else:
                category = self.product_id.categ_id
                while category:
                    if category in discount.product_category_ids:
                        self.sale_discounts += discount
                        break
                    category = category.parent_id

    @api.model
    def existing_discountline(self, values):
        exists = self.search(
            [
                ('order_id', '=', values.get('order_id')),
                ('product_id', '=', values.get('product_id')),
                ('name', '=', values.get('name')),
                ('sale_discount_line', '=', True)
                ]
        )
        equal = self.search(
            [
                ('order_id', '=', values.get('order_id')),
                ('product_id', '=', values.get('product_id')),
                ('name', '=', values.get('name')),
                ('price_unit', '=', values.get('price_unit')),
                ('product_uom_qty', '=', values.get('product_uom_qty')),
                ('sale_discount_line', '=', True)
                ]
        )

        return exists, equal
