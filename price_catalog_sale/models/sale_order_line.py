# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models , api
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    """Override SaleOrderLine to show catalogs prices."""

    _inherit = "sale.order.line"

    currency_id = fields.Many2one(depends=["order_id.currency_id"])

    @api.onchange('product_id')
    def product_id_change(self):
        res = super().product_id_change()
        if not self.product_id:
            return
        if not self.product_id.type == 'service':
            if "P0" not in str(self.product_id.default_code):
                price_exists = self.order_id.price_catalog_id.get_price(
                    self.product_id, self.order_id.date_order
                )
                if price_exists is False:
                    raise ValidationError("You Cant Select this Product."
                                          "Product is not added in this Pricelist")
        return res

    def _get_display_price(self, product):
        """Override to use price catalogs instead of pricelists."""
        price = self.order_id.price_catalog_id.get_price(
            self.product_id, self.order_id.date_order
        )
        if price is False:
            price = super()._get_display_price(product)
        return price
