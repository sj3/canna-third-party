# Copyright 2009-2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Account Move Line XLSX export",
    "version": "13.0.1.1.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "category": "Accounting & Finance",
    "summary": "Journal Items Excel export",
    "depends": ["account", "report_xlsx_helper"],
    "data": [
        "views/assets_backend.xml",
        "report/account_move_line_xlsx.xml",
        "report/account_move_line_xlsx_all.xml",
    ],
    "installable": True,
}
