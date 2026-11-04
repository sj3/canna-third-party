# Copyright 2009-2024 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Fiscal Position Constraints",
    "version": "18.0.1.0.0",
    "category": "Accounting & Finance",
    "website": "https://www.noviat.com/",
    "author": "Noviat",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["account"],
    "data": [
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
    ],
}
