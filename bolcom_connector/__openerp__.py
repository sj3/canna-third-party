# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Odoo connector to bol.com",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "author": "Noviat",
    "depends": ["sale", "stock"],
    "data": [
        "data/ir_cron_data.xml",
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/product_product_views.xml",
        "wizards/bolcom_so_import.xml",
        "wizards/sale_config_settings.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
