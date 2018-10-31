# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Purchase Order Sale Reference',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'summary': 'Add Sale Order references to Purchase Order',
    'depends': [
        'purchase',
        'sale_stock'
    ],
    'data': [
        'views/purchase_order.xml'
    ],
}
