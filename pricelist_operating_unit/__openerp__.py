# -*- coding: utf-8 -*-
# Copyright (C) 2017 Onestein (http://www.onestein.eu/).
# Copyright (C) 2017 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Operating Unit in Pricelists',
    'summary': 'An operating unit (OU) is an organizational entity part of a '
               'company',
    'version': '8.0.1.1.0',
    'author': 'Onestein, Noviat, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/operating-unit',
    'category': 'Sales & Purchases',
    'license': 'AGPL-3',
    'depends': ['product', 'operating_unit'],
    'data': [
        'security/product_pricelist.xml',
        'views/product_pricelist.xml',
        'views/product_pricelist_version.xml',
    ],
    'installable': True,
}
