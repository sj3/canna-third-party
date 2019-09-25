# -*- coding: utf-8 -*-
# Copyright Onestein (https://www.onestein.eu/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openerp.tests.common import TransactionCase


class TestWebDisableExportGroup(TransactionCase):

    def setUp(self):
        super(TestWebDisableExportGroup, self).setUp()
        self.group_a = 'web_disable_export_group.group_a'
        self.group_b = 'web_disable_export_group.group_b'
        self.partner_a = self.env['res.partner'].create({
            'name': 'Test partner A',
        })
        self.partner_b = self.env['res.partner'].create({
            'name': 'Test partner B',
        })

        self.user_a = self.env['res.users'].create({
            'login': 'user_a',
            'partner_id': self.partner_a.id,
            'groups_id': [(4, self.ref(self.group_a))],
        })
        self.user_b = self.env['res.users'].create({
            'login': 'user_b',
            'partner_id': self.partner_b.id,
            'groups_id': [(4, self.ref(self.group_b))],
        })

    def test_may_export(self):
        """Whether the user is allowed to export a set of records or not."""
        self.assertTrue(self.user_a.may_export('res.partner'))
        self.assertFalse(self.user_b.may_export('res.partner'))
