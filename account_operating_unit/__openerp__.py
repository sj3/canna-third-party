# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": 'Accounting with Operating Units',
    "version": "8.0.1.1.1",
    "summary": "Introduces Operating Unit fields in invoices and "
               "Accounting Entries with clearing account",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Noviat,"
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Accounting & Finance",
    "depends": ['account', 'operating_unit'],
    "license": "AGPL-3",
    "data": [
        "security/account_security.xml",
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/account_account_view.xml",
        "views/company_view.xml",
        "views/invoice_view.xml",
        "views/account_invoice_report_view.xml",
        "wizard/account_report_common_view.xml",
        "wizard/account_financial_report_view.xml",
    ],
    "installable": True,
}
