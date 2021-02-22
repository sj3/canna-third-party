# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Operating Unit in CRM Partner Action",
    "version": "13.0.1.0.0",
    "summary": "An operating unit (OU) is an organizational entity part of a "
    "company",
    "author": "Onestein BV, André Schenkels" "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "http://www.onestein.eu",
    "category": "CRM",
    "depends": ["crm_partner_action", "operating_unit"],
    "data": [
        "security/crm_partner_action_security.xml",
        "security/crm_partner_action_group_security.xml",
        "views/crm_partner_action.xml",
        "views/crm_partner_action_group.xml",
    ],
}
