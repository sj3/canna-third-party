# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.multi
    def _check_allow_type_change(self, new_type, context=None):
        """
        allow to reopen a closed account that has journal items
        """
        regular_types = ['other', 'receivable', 'payable', 'liquidity']
        to_check = self
        for account in self:
            self.env.cr.execute(
                "SELECT id FROM account_move_line "
                "WHERE account_id = %s LIMIT 1",
                (account.id,))
            res = self.env.cr.fetchone()
            if res and account.type == 'closed' and new_type in regular_types:
                to_check -= account
        return super(AccountAccount, to_check)._check_allow_type_change(
            new_type, context=context)
