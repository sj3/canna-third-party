# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Web Hidden Element',
    'version': '8.0.1.0.0',
    'category': 'Web',
    'author': 'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/web',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/res_groups.xml',
        'views/web_hidden_template_view.xml',
    ],
    'installable': True,
    'auto_install': False
}
