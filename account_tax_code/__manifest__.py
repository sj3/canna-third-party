# Copyright 2009-2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Tax Code",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": """
        Add 'code' field to taxes
    """,
    "author": "Noviat",
    "website": "https://www.noviat.com/",
    "depends": ["account"],
    "data": [
        "views/account_fiscal_position_views.xml",
        "views/account_move_views.xml",
        "views/account_tax_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
