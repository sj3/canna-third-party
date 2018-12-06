# -*- coding: utf-8 -*-

{
    'name': 'Extended Approval Payment Order',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'category': 'base',
    'depends': [
        'account_payment',
        'base_extended_approval',
    ],
    'data': [
        'views/payment_order.xml',
    ],
    'installable': True,
}
