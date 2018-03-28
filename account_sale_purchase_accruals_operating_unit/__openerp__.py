# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Account Sale Purchase Accruals - Operating Unit support',
    'version': '8.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Accounting & Finance',
    'complexity': 'normal',
    'conflicts': ['account_anglo_saxon'],
    'depends': [
        'account_sale_purchase_accruals',
        'account_operating_unit',
        'purchase_operating_unit',
    ],
    'data': [],
    'installable': True,
}
