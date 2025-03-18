# Copyright 2009-2025 Noviat
# Copyright 2025 Canna
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Split",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat,Canna",
    "website": "https://www.noviat.com",
    "category": "Accounting & Finance",
    "complexity": "normal",
    "summary": "Split Draft Invoices",
    "data": [
        "views/account_move_views.xml",
        "wizards/account_invoice_split_views.xml",
    ],
    "depends": ["account"],
    "installable": True,
}
