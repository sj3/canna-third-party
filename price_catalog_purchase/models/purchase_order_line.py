from odoo import api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrderLine(models.Model):
    """Override PurchaseOrder for catalog prices."""

    _inherit = "purchase.order.line"

    price_catalog_id = fields.Many2one(
        string="Price Catalog",
        comodel_name="price.catalog",
        related="order_id.price_catalog_id"
    )

    @api.onchange("price_catalog_id")
    def _onchange_price_catalog_id(self):
        item_ids = []
        if self.order_id.price_catalog_id:
            self.env["price.catalog.item"].flush(["price", "company_id"])
            self.env.cr.execute(
                """
                SELECT product.id
                FROM price_catalog_item AS item
                INNER JOIN price_subcatalog AS subcatalog

                ON item.subcatalog_id = subcatalog.id
                INNER JOIN product_product AS product
                ON item.product_id = product.id
                WHERE
                    subcatalog.active = True
                    AND subcatalog.catalog_id = %s
                    AND (subcatalog.start_date IS NULL
                         OR subcatalog.start_date <= %s)
                    AND (subcatalog.end_date IS NULL
                         OR subcatalog.end_date >= %s)
                ORDER BY
                    subcatalog.sequence, item.sequence
                """,
                (self.order_id.price_catalog_id.id, self.order_id.date_order, self.order_id.date_order),
            )
            item_ids = [x[0] for x in self.env.cr.fetchall()]
        return {
            "domain": {'product_id': [('id', 'in', item_ids)]},
        }
