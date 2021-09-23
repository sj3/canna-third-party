# Copyright Onestein (http://www.onestein.eu).
# Copyright (C) 2021-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Git Version Info',
    'version': "13.0.1.0.0",
    "author": "Onestein, " "Serpent Consulting Services Pvt. Ltd.",
    'category': 'Tools',
    'website': 'http://www.serpentcs.com',
    'license': "AGPL-3",
    'summary': 'Git Version',
    'depends': ['web'],
    'data': [
             'views/assets.xml',
        ],
    'qweb': [
        "static/src/xml/about_odoo.xml",
    ],
    'installable': True,
}
