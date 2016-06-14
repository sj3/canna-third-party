# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Onestein
#    (<http://www.onestein.eu>).
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

table_renames = [
    ('payment_type', 'payment_mode_type'),
]

model_renames = [
    ('payment.type', 'payment.mode.type'),
]


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    openupgrade.rename_models(cr, model_renames)
    openupgrade.rename_tables(cr, table_renames)
