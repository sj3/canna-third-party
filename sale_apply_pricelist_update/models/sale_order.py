# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, models, _
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def button_dummy(self):
        """
        logic copied from Odoo standard 'product_id_change' method
        """
        err_msg = ''
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for so in self:
            for sol in so.order_line:
                ctx = dict(
                    self.env.context,
                    uom=sol.product_uom.id,
                    date=so.date_order)
                pl = so.pricelist_id.with_context(ctx)
                price_unit = False
                try:
                    price_unit = pl.price_get(
                        sol.product_id.id, sol.product_uom_qty,
                        so.partner_id.id
                    )[pl.id]
                except UserError, e:
                    err_msg += _(
                        "Pricelist lookup failed for product %s ! : "
                    ) % sol.product_id.name + "\n\n"
                    _logger.error(err_msg + str(e))
                if price_unit is False:
                    msg = _(
                        "Cannot find a pricelist line matching "
                        "this product and quantity.\n"
                        "You have to change either the product, "
                        "the quantity or the pricelist.")
                    err_msg += _(
                        "No valid pricelist line found for product %s ! :"
                    ) % sol.product_id.name + msg + "\n\n"
                elif round(price_unit - sol.price_unit, digits):
                    sol.price_unit = price_unit
                if err_msg:
                    raise UserError(err_msg)
        return super(SaleOrder, self).button_dummy()
