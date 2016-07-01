# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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
    if not version:
        return

    # Ensure table exists
    if openupgrade.table_exists(cr, 'banking_export_sdd'):
        cr.execute(
            'ALTER TABLE banking_export_sdd '
            'RENAME TO migration_banking_export_sdd')
    if openupgrade.table_exists(cr, 'account_payment_order_sdd_rel'):
        cr.execute(
            'ALTER TABLE account_payment_order_sdd_rel '
            'RENAME TO migration_account_payment_order_sdd_rel')
