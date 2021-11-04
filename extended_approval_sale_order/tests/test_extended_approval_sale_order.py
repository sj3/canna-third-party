# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.sale.tests.test_sale_common import TestCommonSaleNoChart
from odoo.tests import tagged


@tagged("-at_install", "post_install")
class ExtendedApprovalSaleOrderUnit(TestCommonSaleNoChart):
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
        # Create User 1 with group 1
        self.user1 = self._create_user(
            "user_1", [self.group.id, self.group0.id, self.group1.id], self.company
        )
        # Create User 2 with group 2
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

    def test_01_approval_sale_order(self):
        flow = self.env["extended.approval.flow"].create(
            {"name": "unittest sale order approval", "model": "sale.order"}
        )
        step = self.env["extended.approval.step"].create(
            {"flow_id": flow.id, "group_ids": [self.group1.id]}
        )

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
            "Sale order should be in state 'extended_approval'",
        )

        test_sale.with_user(self.user2.id).action_confirm()
        self.assertEqual(
            test_sale.state,
            "extended_approval",
            "Sale order still be in state 'extended_approval'",
        )

        test_sale.with_user(self.user1.id).action_confirm()
        self.assertEqual(test_sale.state, "sale", "Sale order still be in state 'sale'")

        # trigger recompute
        test_sale._compute_history_ids()
        self.assertEqual(
            len(test_sale.approval_history_ids),
            1,
            "Sale order should have one approval record",
        )

        step.unlink()
        flow.unlink()
