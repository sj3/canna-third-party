# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Bank Statement Import - Advanced',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'website': 'http://www.noviat.com',
    'category': 'Accounting & Finance',
    'depends': [
        'account_bank_statement_import',
        'account_bank_statement_advanced',
    ],
    'data': [
        'wizard/account_bank_statement_import_view.xml',
    ],
    'installable': True,
}
