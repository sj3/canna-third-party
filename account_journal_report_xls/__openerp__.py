# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Financial Journal reports',
    'version': '8.0.0.4.2',
    'license': 'AGPL-3',
    'author': "Noviat,Odoo Community Association (OCA)",
    'category': 'Accounting & Finance',
    'depends': [
        'account_voucher',
        'report_xls',
    ],
    'demo': [],
    'images': [
        'static/description/journal_overview.png',
    ],
    'data': [
        'wizard/print_journal_wizard.xml',
    ],
    'test': [
        'tests/print_journal_by_fiscal_year.yml',
        'tests/print_journal_by_period.yml',
        'tests/export_csv_journal_by_fiscal_year.yml',
        'tests/export_csv_journal_by_period.yml',
    ],
    'installable': True,
}
