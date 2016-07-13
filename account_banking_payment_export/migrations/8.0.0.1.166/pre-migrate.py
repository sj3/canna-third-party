# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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

logger = logging.getLogger('OpenUpgrade.account_payment_extension')

# WARNING check table_exists below if you adjust this dictionary
column_renames = {
    'bank_type_payment_type_rel': [
        ('pay_type_id', None),
        ('bank_type_id', None),
    ],
}

table_renames = [
    ('bank_type_payment_type_rel', None),
    # ('payment_type', None),
]


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    # In case account_payment_extension was installed, set
    # bank_type_payment_type_rel to legacy; assume payment.mode.type
    # and payment.type are not the same.
    if openupgrade.table_exists(cr, 'bank_type_payment_type_rel'):
        logger.info("Found bank_type_payment_type_rel")
        openupgrade.rename_columns(cr, column_renames)
        openupgrade.rename_tables(cr, table_renames)
    cr.execute(
        'SELECT count(attname) FROM pg_attribute '
        'WHERE attrelid = '
        '( SELECT oid FROM pg_class WHERE relname = %s ) '
        'AND attname = %s',
        ('payment_order', 'total'))
    if cr.fetchone()[0] == 0:
        cr.execute('alter table payment_order add column total numeric')
    cr.execute(
        'update payment_order '
        'set total=totals.total '
        'from '
        '(select order_id, sum(amount_currency) total '
        'from payment_line group by order_id) totals '
        'where payment_order.id=totals.order_id')
