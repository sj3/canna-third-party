# -*- coding: utf-8 -*-
# Copyright 2020 Onestein.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Tracked Visibility Report',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Onestein',
    'category': 'Reporting',
    'depends': [
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/tracked_visibility_report.xml',
        'views/menu.xml',
    ],
    'installable': True,
}
