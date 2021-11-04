# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart


@tagged("-at_install", "post_install")
class ExtendedApprovalSaleOrderGroupUnit(TestCommonSaleNoChart):
    def setUp(self):
        super().setUp()
        self.res_users_model = self.env["res.users"].with_context(
            tracking_disable=True, no_reset_password=True
        )

        # Company
        self.company = self.env.ref("base.main_company")

        self.group0 = self.env.ref("base.group_user")
        self.group = self.env.ref("sales_team.group_sale_salesman_all_leads")
        self.group1 = self._create_group("group1")
        self.group2 = self._create_group("group2")

        # Create User 0 without group
        self.user0 = self._create_user(
            "user_0", [self.group.id, self.group0.id], self.company
        )
        # Create User 2 with group 1
        self.user1 = self._create_user(
            "user_1", [self.group.id, self.group0.id, self.group1.id], self.company
        )
        # Create User 2 with group 1
        self.user2 = self._create_user(
            "user_2", [self.group.id, self.group0.id, self.group2.id], self.company
        )

        # set up accounts and products and journals
        self.setUpAdditionalAccounts()
        self.setUpClassicProducts()
        self.setUpAccountJournal()

    def _create_group(self, name, context=None):
        """ Create a user. """
        user = self.env["res.groups"].create({"name": name})
        return user

    def _create_user(self, login, group_ids, company, context=None):
        """ Create a user. """
        user = self.res_users_model.create(
            {
                "name": "Test User",
                "login": login,
                "password": "demo",
                "email": "test@yourcompany.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
                "groups_id": [(6, 0, group_ids)],
            }
        )
        return user

    def test_01_approval_sale_order_group(self):
        flow = self.env["extended.approval.flow"].create(
            {"name": "unittest sale order approval", "model": "sale.order.group"}
        )
        step = self.env["extended.approval.step"].create(
            {"flow_id": flow.id, "group_ids": [self.group1.id]}
        )

        test_sale1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_customer_usd.id,
                "partner_invoice_id": self.partner_customer_usd.id,
                "partner_shipping_id": self.partner_customer_usd.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )
        test_sale2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_customer_usd.id,
                "partner_invoice_id": self.partner_customer_usd.id,
                "partner_shipping_id": self.partner_customer_usd.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )

        test_group = self.env["sale.order.group"].create(
            {
                "state": "draft",
                "sale_order_ids": [(6, 0, [test_sale1.id, test_sale2.id])],
                "partner_id": self.partner_customer_usd.id,
            }
        )

        test_group.with_user(self.user0.id).button_confirm()
        self.assertEqual(
            test_group.state,
            "extended_approval",
            "Sale order group should be in state 'extended_approval'",
        )
        self.assertEqual(
            test_sale1.state, "draft", "Sale order should be in state 'draft'"
        )
        self.assertEqual(
            test_sale2.state, "draft", "Sale order should be in state 'draft'"
        )

        test_group.with_user(self.user2.id).button_confirm()
        self.assertEqual(
            test_group.state,
            "extended_approval",
            "Sale order group should still be in state 'extended_approval'",
        )
        self.assertEqual(
            test_sale1.state, "draft", "Sale order should still be in state 'draft'"
        )
        self.assertEqual(
            test_sale2.state, "draft", "Sale order should still be in state 'draft'"
        )

        test_group.with_user(self.user1.id).button_confirm()
        self.assertEqual(
            test_group.state, "confirm", "Sale order group should be in state 'confirm'"
        )
        self.assertEqual(
            test_sale1.state, "sale", "Sale order should be in state 'sale'"
        )
        self.assertEqual(
            test_sale2.state, "sale", "Sale order should be in state 'sale'"
        )

        step.unlink()
        flow.unlink()

    def test_02_approval_sale_order_group_order_interaction(self):
        sale_flow = self.env["extended.approval.flow"].create(
            {"name": "unittest sale order approval", "model": "sale.order"}
        )
        sale_step = self.env["extended.approval.step"].create(
            {"flow_id": sale_flow.id, "group_ids": [self.group1.id]}
        )

        # First test sale order approval flow: sale order should go into approval flow

        test_sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner_customer_usd.id,
                "partner_invoice_id": self.partner_customer_usd.id,
                "partner_shipping_id": self.partner_customer_usd.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )

        test_sale.with_user(self.user0.id).action_confirm()
        self.assertEqual(
            test_sale.state,
            "extended_approval",
            "Sale order should be in state extended_approval",
        )

        # Then test sale order group approval flow: sale order
        # approval flow should be bypassed.

        flow = self.env["extended.approval.flow"].create(
            {"name": "unittest sale order approval", "model": "sale.order.group"}
        )
        step = self.env["extended.approval.step"].create(
            {"flow_id": flow.id, "group_ids": [self.group1.id]}
        )

        test_sale1 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_customer_usd.id,
                "partner_invoice_id": self.partner_customer_usd.id,
                "partner_shipping_id": self.partner_customer_usd.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )
        test_sale2 = self.env["sale.order"].create(
            {
                "partner_id": self.partner_customer_usd.id,
                "partner_invoice_id": self.partner_customer_usd.id,
                "partner_shipping_id": self.partner_customer_usd.id,
                "pricelist_id": self.pricelist_usd.id,
            }
        )

        test_group = self.env["sale.order.group"].create(
            {
                "state": "draft",
                "sale_order_ids": [(6, 0, [test_sale1.id, test_sale2.id])],
                "partner_id": self.partner_customer_usd.id,
            }
        )

        test_group.with_user(self.user0.id).button_confirm()
        self.assertEqual(
            test_group.state,
            "extended_approval",
            "Sale order group should be in state 'extended_approval'",
        )
        self.assertEqual(
            test_sale1.state, "draft", "Sale order should be in state 'draft'"
        )
        self.assertEqual(
            test_sale2.state, "draft", "Sale order should be in state 'draft'"
        )

        test_group.with_user(self.user2.id).button_confirm()
        self.assertEqual(
            test_group.state,
            "extended_approval",
            "Sale order group should still be in state 'extended_approval'",
        )
        self.assertEqual(
            test_sale1.state, "draft", "Sale order should still be in state 'draft'"
        )
        self.assertEqual(
            test_sale2.state, "draft", "Sale order should still be in state 'draft'"
        )

        test_group.with_user(self.user1.id).button_confirm()
        self.assertEqual(
            test_group.state, "confirm", "Sale order group should be in state 'confirm'"
        )
        self.assertEqual(
            test_sale1.state, "sale", "Sale order should be in state 'sale'"
        )
        self.assertEqual(
            test_sale2.state, "sale", "Sale order should be in state 'sale'"
        )

        step.unlink()
        flow.unlink()
        sale_step.unlink()
        sale_flow.unlink()
