# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Onestein (http://www.onestein.eu).
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
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

from openerp import api, SUPERUSER_ID
from openupgradelib import openupgrade
import logging

logger = logging.getLogger('OpenUpgrade')


def create_discounts(cr, env):
    discount_obj = env['sale.discount']
    legacy_product_pricelist_bulk = openupgrade.get_legacy_name(
        'product_pricelist_bulk')
    legacy_discount = openupgrade.get_legacy_name('priority')
    legacy_minimum_amount = openupgrade.get_legacy_name('minimum_amount')
    legacy_pricelist_id = openupgrade.get_legacy_name('pricelist_id')

    openupgrade.logged_query(
        cr,
        """
        SELECT id, {}, {}, {} FROM {}
        """.format(
            legacy_discount, legacy_minimum_amount,
            legacy_pricelist_id,
            legacy_product_pricelist_bulk
        )
    )
    bulks = cr.fetchall()
    for bulk in bulks:
        # TODO make name depend on type of discount (e.g.
        # product.pricelist.bulk/payment_type/global_discount)

        rule_vals = {
            # 'company_id': ,
            # 'sequence': ,
            # 'sale_discount_id': , # Inverse of rules
            'discount_type': 'perc',
            'discount': bulk[1],
            'max_base': bulk[2],
        }
        vals = {
            'id': bulk[0],
            # Assume empty table, so copy source ids should be safe.
            'name': '{} {}{}'.format('Discount', bulk[1], '%'),
            # 'start_date': ,
            # 'end_date': ,
            'active': True,
            # 'product_id': ,
            'discount_base': 'sale_line',
            'pricelists': (4, bulk[3], 0),
            'rules': (0, 0, rule_vals),
        }
        discount_obj.create(vals)


def add_discounts(cr, env):
    """Add discounts created in create_discounts to sale.order.line

    Find 'the applicable product_pricelist_bulk.discount'
    For each line, check if its category (categ_id) has
    apply_bulk_discount (legacy) set.
    If so, get the discount value from product.pricelist.bulk
    Discount depends on pricelist too (field pricelist_id, whether the
    product is in the pricelist does not matter)
    """
    order_obj = env.get('sale.order')
    line_obj = env.get('sale.order.line')
    discount_obj = env.get('sale.discount')
    gdc_legacy = openupgrade.get_legacy_name('global_discount_confirm')
    discount_legacy = openupgrade.get_legacy_name('discount')

    minimum_discount = 1
    orders = order_obj.search(cr, SUPERUSER_ID, [(gdc_legacy, '=', False)])
    lines = line_obj.search(cr, SUPERUSER_ID, [
        (discount_legacy, '>=', minimum_discount),
        ('order_id', 'not in', orders)
    ])
    for line in lines:
        # Note: Should not use line.discount as we should separate bulk and
        # type disounts.
        if line.product_id.categ_id.apply_bulk_discount:
            highest_subtotal = 0
            minimum_amount = False
            discount_percentage = False
            for bulk_discount in \
                    line.product_id.pricelist_id.bulk_order_discount_ids:
                gross_subtotal = line.price_unit * line.product_uom_qty
                if gross_subtotal > highest_subtotal and \
                                gross_subtotal >= bulk_discount.minimum_amount:
                    highest_subtotal = gross_subtotal
                    minimum_amount = bulk_discount.minimum_amount
                    discount_percentage = bulk_discount.discount
                else:
                    break
            if minimum_amount:
                # Get the relevant discount object
                # Optimize: use xmlid?
                discount_id = discount_obj.search(cr, SUPERUSER_ID, [
                    ('max_base', '=', minimum_amount),
                    ('discount', '=', discount_percentage)
                ])
                assert len(discount_id) == 1
            sale_discounts = {'sale_discounts': (4, discount_id, 0)}
            line.write(sale_discounts)

        legacy_discounts = line.product_id.pricelist_id.bulk_order_discount_ids[
            0]
        # TODO case when there are multiple discounts

        # TODO Global discount override
        # TODO additional discounts based on payment term


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        legacy_product_pricelist_bulk = openupgrade.get_legacy_name(
            'legacy_product_pricelist_bulk')
        # Custom for migration staffel discounts:
        if legacy_product_pricelist_bulk:
            create_discounts(cr, env)
            add_discounts(cr, env)
