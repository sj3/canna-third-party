# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
#    Copyright (c) 2009-2016 Onestein BV (www.onestein.eu).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Account Operating Unit Dimension Policy',
    'version': '8.0.1.1.2',
    'license': 'AGPL-3',
    'author': 'Noviat, Onestein',
    'category': 'Operating Unit',
    'summary': 'Enforce Analytic Dimension Policy on Operating Unit',
    'depends': [
        'account_analytic_dimension_policy',
        'account_bank_statement_operating_unit',
    ],
    'data': [
        'views/account_invoice.xml',
        'views/account_move.xml',
        'views/account_move_line.xml',
        'views/assets_backend.xml',
    ],
}
