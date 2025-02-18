# Copyright 2009-2025 Noviat (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from odoo.tests.common import Form, TransactionCase


class TestPalletDiscount(TransactionCase):
    def setUp(self):
        super().setUp()
        self.so_obj = self.env["sale.order"]
        self.sd_obj = self.env["sale.discount"]
        self.sdr_obj = self.env["sale.discount.rule"]
        self.partner = self.env.ref("base.res_partner_2")
        self.date_order = datetime.strptime(
            time.strftime("%Y-02-01 08:30:00"), "%Y-%m-%d %H:%M:%S"
        )
        self.pallet_discount = self.env.ref(
            "sale_discount_advanced_pallet.sale_discount_pallet"
        )

    def test_pallet_discount(self):
        discount_ids = [(6, 0, [self.pallet_discount.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_7"),
                            "name": "Line 1",
                            "product_uom_qty": 6,
                            "price_unit": 100,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_7"),
                            "name": "Line 2",
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.pallet_discount)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 700, "Total amount should be 700.00")

        with so_form.order_line.edit(1) as line_form:
            line_form.product_uom_qty = 4
            line_form.price_unit = 100
        so_form.save()
        self.assertEquals(so.amount_untaxed, 900, "Total amount should be 900.00")

        with so_form.order_line.edit(1) as line_form:
            line_form.product_uom_qty = 14
            line_form.price_unit = 100
        so_form.save()
        self.assertEquals(so.amount_untaxed, 1600, "Total amount should be 1600.00")
