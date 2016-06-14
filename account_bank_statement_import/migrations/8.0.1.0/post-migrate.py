# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
#    Copyright (C) 2016 Onestein (www.onestein.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openupgradelib import openupgrade
import logging
logger = logging.getLogger('OpenUpgrade')


@openupgrade.migrate(no_version=False)
def migrate(cr, version):
    # if we end up here, we migrate from 7.0's account_banking
    # set transaction ids, taking care to enforce uniqueness

    # Ensure the column exists.
    cr.execute(
        """
        SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = 'account_bank_statement_line'
        AND column_name = 'trans';
        """
    )
    res = cr.fetchone()
    if res == 1:
        logger.info('account_bank_statement_line', res)
        cr.execute(
            """update account_bank_statement_line l set unique_import_id=l1.trans
            from (
                select distinct
                first_value(id) over (partition by trans) id, trans
                from account_bank_statement_line
            ) l1
            where l.id=l1.id""")
