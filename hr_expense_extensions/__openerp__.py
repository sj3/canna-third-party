# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Expense module extensions',
    'version': '8.0.1.0.1',
    'license': 'AGPL-3',
    'author': 'Noviat',
    'category': 'Human Resources',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'views/account_journal.xml',
        'views/hr_expense_expense.xml',
        'wizard/hr_expense_expense_accounting_wizard.xml',
        'wizard/hr_expense_line_product_wizard.xml',
    ],
    'installable': True,
}
