# -*- encoding: utf-8 -*-
from openerp import SUPERUSER_ID, api


def migrate(cr, version):
    with api.Environment.manage():
        cr.execute(
            """
        ALTER TABLE account_move_line ADD COLUMN signed_balance numeric;
        UPDATE account_move_line
        SET signed_balance = debit - credit
        WHERE signed_balance IS NULL;
        """
        )
