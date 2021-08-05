# © 2021 Startx BV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)

from odoo.tests import common, tagged


@tagged("-at_install", "post_install")
class ExtendedApprovalPartnerUnit(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.res_users_model = self.env["res.users"].with_context(
            tracking_disable=True, no_reset_password=True
        )

        # Company
        self.company = self.env.ref("base.main_company")

        self.group0 = self.env.ref("base.group_user")
        self.group = self.env.ref("base.group_partner_manager")
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

    def test_01_approval_partner(self):
        flow = self.env["extended.approval.flow"].create(
            {"name": "unittest partner approval", "model": "res.partner"}
        )
        step = self.env["extended.approval.step"].create(
            {"flow_id": flow.id, "group_ids": [self.group1.id]}
        )

        test_partner = self.env["res.partner"].create({"name": "test 1"})

        test_partner.with_user(self.user0.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state,
            "extended_approval",
            "Partner should be in state extended_approval",
        )

        test_partner.with_user(self.user1.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state, "confirmed", "Partner should be in state confirmed"
        )

        # trigger recompute
        test_partner._compute_history_ids()
        self.assertEqual(
            len(test_partner.approval_history_ids),
            1,
            "Partner should have one approval record",
        )

        step.unlink()
        flow.unlink()

    def test_01_multistep_approval_partner(self):
        flow = self.env["extended.approval.flow"].create(
            {"name": "unittest partner approval", "model": "res.partner"}
        )
        step1 = self.env["extended.approval.step"].create(
            {
                "flow_id": flow.id,
                # 'condition': '',
                "sequence": 10,
                "group_ids": [self.group1.id],
            }
        )
        step2 = self.env["extended.approval.step"].create(
            {
                "flow_id": flow.id,
                # 'condition': '',
                "sequence": 20,
                "group_ids": [self.group2.id],
            }
        )

        test_partner = self.env["res.partner"].create({"name": "test 2"})

        test_partner.with_user(self.user0.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state,
            "extended_approval",
            "Partner should be in state extended_approval",
        )
        # trigger recompute
        test_partner._compute_history_ids()
        self.assertEqual(
            len(test_partner.approval_history_ids),
            0,
            "Partner should have 0 approval record",
        )

        test_partner.with_user(self.user2.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state,
            "extended_approval",
            "Partner should be in state extended_approval",
        )
        # trigger recompute
        test_partner._compute_history_ids()
        self.assertEqual(
            len(test_partner.approval_history_ids),
            0,
            "Partner should have 0 approval record",
        )

        test_partner.with_user(self.user1.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state,
            "extended_approval",
            "Partner should be in state extended_approval",
        )
        # trigger recompute
        test_partner._compute_history_ids()
        self.assertEqual(
            len(test_partner.approval_history_ids),
            1,
            "Partner should have 1 approval record",
        )

        test_partner.with_user(self.user2.id).set_state_to_confirmed()
        self.assertEqual(
            test_partner.state, "confirmed", "Partner should be in state confirmed"
        )
        # trigger recompute
        test_partner._compute_history_ids()
        self.assertEqual(
            len(test_partner.approval_history_ids),
            2,
            "Partner should have 2 approval records",
        )

        step1.unlink()
        step2.unlink()
        flow.unlink()
