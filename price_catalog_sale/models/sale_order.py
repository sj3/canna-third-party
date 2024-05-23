# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    """Override SaleOrder for picking catalogs."""

    _inherit = "sale.order"

    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        domain=[("catalog_type", "=", "sale")],
        required=True,
        default=lambda r: r._default_price_catalog_id(),
    )
    currency_id = fields.Many2one(
        string="Currency", compute="_compute_currency_id", required=True, related=False
    )

    @api.depends("price_catalog_id", "pricelist_id")
    def _compute_currency_id(self):
        for so in self:
            so.currency_id = (
                so.price_catalog_id.currency_id
                or so.pricelist_id.currency_id
                or so.company_id.currency_id
            )

    def _default_price_catalog_id(self):
        return (
            self.env.ref("price_catalog.price_catalog_default", False)
            and self.env.ref("price_catalog.price_catalog_default")
            or self.env["price.catalog"]
        )

    @api.onchange("partner_id")
    def onchange_partner_id(self):
        res = super().onchange_partner_id()
        self.price_catalog_id = self.partner_id.commercial_partner_id.sale_catalog_id
        return res

    def _prepare_invoice(self):
        vals = super()._prepare_invoice()
        vals["currency_id"] = self.currency_id.id
        return vals

    @api.onchange("price_catalog_id")
    def _onchange_catalog(self):
        """When the Price Catalog field is changed, set the Order's currency
        to match that of the Price Catalog and update price according to the
        new vendor's price catalog.
        """
        # Note: cascades to lines
        if self.price_catalog_id:
            for line in self.order_line:
                if not line.product_id.type == 'service':
                    if "P0" not in str(line.product_id.default_code):
                        price_exists = self.price_catalog_id.get_price(
                            line.product_id, self.date_order
                        )
                        if not price_exists:
                            raise ValidationError(
                                _("%s : Product is not added in the Pricelist") % (line.product_id.name))
        else:
            if self.order_line:
                raise ValidationError(_("Product is not added in the Pricelist"))
