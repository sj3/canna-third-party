# Copyright 2009-2022 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Expense module extensions",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "category": "Human Resources",
    "depends": ["hr_expense"],
    "data": [
        "views/account_journal_views.xml",
        "views/hr_expense_sheet_views.xml",
        "wizards/hr_expense_line_product_wizard_views.xml",
    ],
    "installable": True,
}
