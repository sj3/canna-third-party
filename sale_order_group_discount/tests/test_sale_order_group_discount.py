# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2022 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase

from dateutil.relativedelta import relativedelta


class TestSaleOrderGroupDiscount(TransactionCase):

    def setUp(self):
        super().setUp()
        self.so_obj = self.env["sale.order"]
        self.sd_obj = self.env["sale.discount"]
        self.sdr_obj = self.env["sale.discount.rule"]
        self.partner = self.env.ref("base.res_partner_2")
        self.date_order = datetime.strptime(
            time.strftime("%Y-02-01 08:30:00"), "%Y-%m-%d %H:%M:%S"
        )
        self.discount_order = self.env.ref(
            "sale_order_group_discount.sale_discount_on_sale_order_group"
        )

    def test_discount_on_sale_order_group(self):
        discount_ids = [(6, 0, [self.discount_order.id])]
        so1 = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
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
        with Form(so1) as so_form:
            so_form.discount_ids.add(self.discount_order)
        so1 = so_form.save()
        self.assertEquals(so1.amount_total, 950, "Total amount should be 950.00")

        so2 = self.so_obj.with_context({"so_discount_ids": discount_ids}).create(
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
        with Form(so2) as so_form:
            so_form.discount_ids.add(self.discount_order)
        so2 = so_form.save()
        self.assertEquals(so2.amount_total, 950, "Total amount should be 950.00")

        group_form = Form(self.env['sale.order.group.create'].with_context(active_ids=[so1.id, so2.id]))
        group_wizard = group_form.save()
        group_wizard.group_orders()

        so1.sale_order_group_id.calculate_discount()

        self.assertEquals(so1.amount_total, 712.5, "Total amount should be 712.50")
        self.assertEquals(so2.amount_total, 712.5, "Total amount should be 712.50")
