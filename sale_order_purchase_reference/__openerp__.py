# -*- coding: utf-8 -*-
# Copyright 2015 Onestein BV (www.onestein.eu).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Sale Order Purchase Reference',
    'version': '8.0.0.0.1',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'website': 'http://www.onestein.nl',
    'category': 'Sale',
    'complexity': 'normal',
    'summary': 'Sale Order Purchase Reference',
    'depends': [
        'purchase_order_sale_reference',
    ],
    'data': [
        'views/sale_order.xml',
        'views/purchase_order.xml',
    ],
}
