# Copyright (C) 2022 Startx bv (<http://www.startx.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import time
from datetime import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, TransactionCase

from dateutil.relativedelta import relativedelta


class TestSaleOrderGroup(TransactionCase):

    def setUp(self):
        super().setUp()
        self.so_obj = self.env["sale.order"]
        self.partner = self.env.ref("base.res_partner_2")
        self.date_order = datetime.strptime(
            time.strftime("%Y-02-01 08:30:00"), "%Y-%m-%d %H:%M:%S"
        )

    def test_sale_order_group(self):
        so1 = self.so_obj.create(
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
        self.assertEquals(so1.amount_total, 950, "Total amount should be 950.00")
        self.assertEqual(self.env['sale.order.group'], so1.sale_order_group_id, "Sale order group should be unset")
        
        so2 = self.so_obj.create(
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
        self.assertEquals(so2.amount_total, 950, "Total amount should be 950.00")
        self.assertEqual(self.env['sale.order.group'], so2.sale_order_group_id, "Sale order group should be unset")
        
        group_form = Form(self.env['sale.order.group.create'].with_context(active_ids=[so1.id, so2.id]))
        group_wizard = group_form.save()
        
        group_wizard.group_orders()

        self.assertNotEqual(self.env['sale.order.group'], so1.sale_order_group_id, "Sale order group should be set")
        self.assertNotEqual(self.env['sale.order.group'], so2.sale_order_group_id, "Sale order group should be set")

        so1.sale_order_group_id.button_confirm()

        so1.sale_order_group_id.button_cancel()        
