# See LICENSE file for full copyright and licensing details.

{
    "name": "CRM Visit",
    "version": "13.0.1.0.0",
    "website": "https://www.onestein.eu",
    "license": "LGPL-3",
    "category": "CRM",
    "summary": "",
    "author": "Onestein BV, André Schenkels, " "Serpent Consulting Services Pvt. Ltd.",
    "depends": ["sale_management"],
    "data": [
        "security/crm_visit_security.xml",
        "security/ir.model.access.csv",
        "data/crm_visit_sequence.xml",
        "views/menu_items.xml",
        "views/crm_visit_feeling.xml",
        "views/crm_visit_reason.xml",
        "views/crm_visit.xml",
        "views/res_partner.xml",
    ],
    "installable": True,
}
