# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 ICTSTUDIO (<http://www.ictstudio.eu>).
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

{
    'name': 'Operating Unit - Easy Switch Operating Unit',
    'version': '8.0.1.0.0',
    'category': 'web',
    'author': "ICTSTUDIO, André Schenkels, GRAP,Odoo Community Association (OCA)",
    'website': 'http://www.ictstudio.eu',
    'license': 'AGPL-3',
    'depends': [
        'web',
        'operating_unit'
    ],
    'data': [
        'view/res_users.xml',
    ],
    'qweb': [
        'static/src/xml/switch_operating_unit.xml',
    ],

}