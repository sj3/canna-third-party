# Copyright 2009-2017 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Stock Level Excel export",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat, " "Serpent Consulting Services Pvt. Ltd.",
    "website": "http://www.noviat.com",
    "category": "Warehouse Management",
    "depends": ["stock", "stock_account", "report_xlsx"],
    "data": [
        "wizard/wiz_export_stock_level.xml",
        "views/action_manager.xml",
        "views/partner_views.xml",
    ],
    "installable": True,
}
