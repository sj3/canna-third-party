# Copyright 2016-2020 Onestein B.V.
# Copyright 2025 Calin
# Copyright 2025 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Price Catalog Importer",
    "summary": "Import Catalog Style Pricelists",
    "version": "13.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "website": "https://onestein.nl/",
    "author": "Noviat,Onestein,Calin",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["price_catalog_sale", "price_catalog_purchase"],
    "external_dependencies": {"python": ["xlsxwriter", "xlrd"]},
    "data": ["wizards/import_price_catalog_views.xml", "views/menu.xml"],
}
