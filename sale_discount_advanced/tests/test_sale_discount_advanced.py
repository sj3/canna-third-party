# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2023 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase

from dateutil.relativedelta import relativedelta


class TestSaleDiscountAdvanced(TransactionCase):
    def setUp(self):
        super().setUp()
        self.so_obj = self.env["sale.order"]
        self.sd_obj = self.env["sale.discount"]
        self.sdr_obj = self.env["sale.discount.rule"]
        self.partner = self.env.ref("base.res_partner_2")
        self.date_order = datetime.strptime(
            time.strftime("%Y-02-01 08:30:00"), "%Y-%m-%d %H:%M:%S"
        )
        self.discount_order_1 = self.env.ref(
            "sale_discount_advanced.sale_discount_on_sale_order_1"
        )
        self.discount_order_2 = self.env.ref(
            "sale_discount_advanced.sale_discount_on_sale_order_2"
        )
        self.discount_line = self.env.ref(
            "sale_discount_advanced.sale_discount_on_sale_order_line"
        )

    def test_lower_min_base_threshold(self):
        discount_ids = [(6, 0, [self.discount_order_1.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 950,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 950, "Total amount should be 950.00")

        discount_ids = [(6, 0, [self.discount_line.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_line)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 100, "Total amount should be 100.00")

    def test_higher_min_base_threshold(self):
        discount_ids = [(6, 0, [self.discount_order_1.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 1000,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 750, "Total amount should be 750.00")

        discount_ids = [(6, 0, [self.discount_line.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 750,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_line)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 675, "Total amount should be 675.00")

    def test_next_min_base_threshold(self):
        discount_ids = [(6, 0, [self.discount_order_1.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 1500,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 1125, "Total amount should be 1125.00")

        discount_ids = [(6, 0, [self.discount_order_1.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "discount_ids": discount_ids,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 3000,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 1500, "Total amount should be 1500.00")

    def test_discount_out_of_date_range(self):
        discount_ids = [(6, 0, [self.discount_order_1.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order - relativedelta(years=1),
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 3000,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 3000, "Total amount should be 3000.00")

    def test_excluded_products(self):
        excluded_by_product = self.ref(
            "sale_discount_advanced.product_product_consultant"
        )
        excluded_by_category = self.ref("product.product_product_11")
        discount_ids = [(6, 0, [self.discount_line.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": excluded_by_category,
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 3000,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": excluded_by_product,
                            "name": "Line 2",
                            "product_uom_qty": 1,
                            "price_unit": 3000,
                        },
                    ),
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_line)
        so_form.save()
        self.assertEquals(
            so.amount_untaxed, 6000, "Total untaxed amount should be 6000.00"
        )

    def test_exclusive_discount(self):
        discount_ids = [(6, 0, [self.discount_order_1.id, self.discount_line.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 1000.00,
                        },
                    )
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
            so_form.discount_ids.add(self.discount_line)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 925.00, "Total amount should be 925.00")

    def test_multiple_discounts(self):
        # Scenario 1:
        # - 2 discount objects type 'sale_order'
        # - 2 sale order lines
        # The total order volume triggers the 25% of discount object 1
        # The second line trigger on top of this the 50% discount on the product
        # Result:
        # Discount: 950.00 * 0.25 + 100.00 * 0.75 = 312.50
        # Net order amount: 737.50
        discount_ids = [(6, 0, [self.discount_order_1.id, self.discount_order_2.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref(
                                "sale_discount_advanced.product_product_consultant"
                            ),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 950,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 2",
                            "product_uom_qty": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
            so_form.discount_ids.add(self.discount_order_2)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 737.50, "Total amount should be 737.50")

        # Scenario 2:
        # - 2 discount objects types 'sale_order' and 'sale_line'
        #   The 'sale_line' discount is 'Exclusive Always'
        # - 2 sale order lines
        # The total order volume triggers the 25% of discount object 1
        # The second line triggers a 75.00 amount exclusive discount on line 2
        # Result:
        # Discount: 950.00 * 0.25 + 75.00 = 312.50
        # Net SO amount: 787.50
        discount_ids = [(6, 0, [self.discount_order_1.id, self.discount_line.id])]
        so = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
            {
                "partner_id": self.partner.id,
                "date_order": self.date_order,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref(
                                "sale_discount_advanced.product_product_consultant"
                            ),
                            "name": "Line 1",
                            "product_uom_qty": 1,
                            "price_unit": 950,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.ref("product.product_product_24"),
                            "name": "Line 2",
                            "product_uom_qty": 1,
                            "price_unit": 150,
                        },
                    ),
                ],
            }
        )
        with Form(so) as so_form:
            so_form.discount_ids.add(self.discount_order_1)
            so_form.discount_ids.add(self.discount_line)
        so_form.save()
        self.assertEquals(so.amount_untaxed, 787.50, "Total amount should be 787.50")

    def test_constraints_sale_discount(self):
        with self.assertRaises(ValidationError):
            self.sd_obj.create(
                {
                    "name": "Discount",
                    "start_date": "2013-01-01",
                    "end_date": "2012-01-01",
                }
            )

    def test_constraints_sale_discount_rule(self):
        sd = self.sd_obj.create(
            {"name": "Discount", "start_date": "2012-01-01", "end_date": "2013-01-01"}
        )
        # Test lower max
        with self.assertRaises(ValidationError):
            self.sdr_obj.create(
                {
                    "sale_discount_id": sd.id,
                    "discount_type": "perc",
                    "min_base": 200,
                    "max_base": 100,
                    "discount_pct": 25,
                }
            )
        # Test < 0 discount
        with self.assertRaises(ValidationError):
            self.sdr_obj.create(
                {
                    "sale_discount_id": sd.id,
                    "discount_type": "amnt",
                    "min_base": 100,
                    "max_base": 200,
                    "discount_amount": -1,
                }
            )
        # Test > 100% discount
        with self.assertRaises(ValidationError):
            self.sdr_obj.create(
                {
                    "sale_discount_id": sd.id,
                    "discount_type": "perc",
                    "min_base": 100,
                    "max_base": 200,
                    "discount_pct": 110,
                }
            )
