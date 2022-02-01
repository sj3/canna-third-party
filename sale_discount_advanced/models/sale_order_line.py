# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2022 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Discount Engine(s)",
        help="Discount engines used for sale order line discount calculation.",
    )
    applied_sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_line_applied_sale_discount_rel",
        column1="sale_line_id",
        column2="discount_id",
        string="Applied Discount Engine(s)",
        readonly=True,
        help="This field contains the subset of the discount enginges "
        "with a calculated discount percent > 0.",
    )

    def _get_sale_discounts(self):
        self.ensure_one()
        discounts = self.env["sale.discount"]
        if not self.product_id:
            return discounts
        date_order = self.order_id.date_order
        for discount in self.order_id.discount_ids:
            if discount._check_product_filter(
                self.product_id
            ) and discount._check_active_date(check_date=date_order):
                discounts += discount
        return discounts
