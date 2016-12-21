# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Account Journal Inactive',
    'summary': 'Add active flag to Financial Journals',
    'author': 'Noviat',
    'category': 'Accounting & Finance',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/account_journal.xml',
    ],
    'installable': True,
}
