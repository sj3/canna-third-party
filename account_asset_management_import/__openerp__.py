# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Fixed Assets import',
    'version': '8.0.0.0.3',
    'license': 'AGPL-3',
    'author': "Noviat,Odoo Community Association (OCA)",
    'website': 'http://www.noviat.com',
    'category': 'Accounting & Finance',
    'depends': [
        'account_asset_management',
    ],
    'data': [
        'wizard/fixed_asset_import.xml'
    ],
    'installable': True,
}
