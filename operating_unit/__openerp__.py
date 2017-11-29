# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# © 2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Operating Unit",
    "summary": "An operating unit (OU) is an organizational entity part of a "
               "company",
    "version": "8.0.1.3.0",
    "author": "Eficent Business and IT Consulting Services S.L., "
              "Serpent Consulting Services Pvt. Ltd.,"
              "Noviat,"
              "Odoo Community Association (OCA)",
    "website": "http://www.eficent.com",
    "category": "Accounting and finance",
    "depends": ["base"],
    "license": "AGPL-3",
    "data": [
        "security/operating_unit.xml",
        "security/res_partner.xml",
        "security/ir.model.access.csv",
        "views/ir_property.xml",
        "views/operating_unit.xml",
        "views/res_partner.xml",
        "views/res_users.xml",
        "data/operating_unit.xml",
    ],
    'demo': [
        "demo/operating_unit_demo.xml"
    ],
    'installable': True,
}
