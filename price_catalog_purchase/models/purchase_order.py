# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    """Override PurchaseOrder for catalog prices."""

    _inherit = "purchase.order"

    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        domain=[("catalog_type", "=", "purchase")],
    )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        super().onchange_partner_id()
        self.price_catalog_id = (
            self.partner_id.commercial_partner_id.purchase_catalog_id
        )
        # when changing between two partners with the same price catalog
        # _onchange_catalog is not called, allowing a wrong currency to be set.
        self._onchange_catalog()

    @api.onchange("price_catalog_id")
    def _onchange_catalog(self):
        """When the Price Catalog field is changed, set the Order's currency
        to match that of the Price Catalog and update price according to the
        new vendor's price catalog.
        """
        # Note: cascades to lines
        if self.price_catalog_id.currency_id:
            self.currency_id = self.price_catalog_id.currency_id
        else:
            self.currency_id = self.partner_id.property_purchase_currency_id.id or self.env.company.currency_id.id
        if self.price_catalog_id:
            for line in self.order_line:
                line.price_unit = self.price_catalog_id.get_price(
                    line.product_id, self.date_order
                )


class PurchaseOrderLine(models.Model):
    """Override PurchaseOrderLine for catalog prices."""

    _inherit = "purchase.order.line"

    @api.onchange("product_qty", "product_uom")
    def _onchange_quantity(self):
        """Override method to use catalog prices instead of price lists."""
        res = super()._onchange_quantity()
        self.price_unit = self.order_id.price_catalog_id.get_price(
            self.product_id, self.order_id.date_order
        )
        return res

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super().onchange_product_id()
        if not self.product_id:
            return
        if not self.product_id.type == 'service':
            price_exists = self.order_id.price_catalog_id.get_price(
                self.product_id, self.order_id.date_order
            )
            if price_exists is False:
                raise ValidationError("You Cant Select this Product."
                                      "Product is not added in this Pricelist")
        return res
