# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, models, _
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def button_dummy(self):
        """
        logic copied from Odoo standard 'product_id_change' method
        """
        digits = self.env['decimal.precision'].precision_get('Product Price')
        for po in self:
            for pol in po.order_line:
                price_unit = self._get_product_price_unit(pol)
                if round(price_unit - pol.price_unit, digits):
                    pol.price_unit = price_unit
        return super(PurchaseOrder, self).button_dummy()

    def _get_product_price_unit(self, pol):
        err_msg = ''
        po = pol.order_id
        if not pol.product_id:
            return pol.price_unit
        ctx = dict(
            self.env.context,
            uom=pol.product_uom.id,
            date=po.date_order)
        pl = po.pricelist_id.with_context(ctx)
        price_unit = False
        try:
            price_unit = pl.price_get(
                pol.product_id.id, pol.product_qty,
                po.partner_id.id
            )[pl.id]
        except UserError, e:
            err_msg += _(
                "Pricelist lookup failed for product %s ! : "
            ) % pol.product_id.name + "\n\n"
            _logger.error(err_msg + str(e))
        if price_unit is False:
            msg = _(
                "Cannot find a pricelist line matching "
                "this product and quantity.\n"
                "You have to change either the product, "
                "the quantity or the pricelist.")
            err_msg += _(
                "No valid pricelist line found for product %s ! :"
            ) % pol.product_id.name + msg + "\n\n"
            _logger.error(err_msg)
        price_unit = price_unit or pol.product_id.standard_price or 0.0
        return price_unit
