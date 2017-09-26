# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Operating Unit in Pricelists",
    "summary": "An operating unit (OU) is an organizational entity part of a "
               "company",
    "version": "8.0.1.0.0",
    "author": "Eficent, Serpent Consulting Services Pvt. Ltd., "
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Generic Modules/Sales & Purchases",
    "license": "AGPL-3",
    "depends": ["product", "operating_unit"],
    "data": [
        "security/pricelist_security.xml",
        "views/pricelist_view.xml",
        "views/pricelist_version_view.xml",
    ],
    'installable': True,
}
