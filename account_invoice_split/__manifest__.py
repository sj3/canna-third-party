# Copyright 2025 Noviat
# Copyright 2025 Canna
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Account Invoice Split',
    'version': '13.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Noviat,Canna',
    'category': 'Accounting & Finance',
    'summary': 'Split Draft Invoices',
    'data': [
        'views/account_move_views.xml',
        'wizard/account_move_split.xml',
        ],
    'depends': ['canna_invoice'],
    'installable': True
}
