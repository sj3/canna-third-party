# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{'name': 'Users Groups Analysis (xls)',
 'author': 'Onestein',
 'website': 'http://www.onestein.eu',
 'version': '8.0.1.0.0',
 'license': 'AGPL-3',
 'category': 'Hidden',
 'depends': [
     'base',
 ],
 'data': [
     'wizard/user_group_analysis_xls.xml',
 ],
 'external_dependencies': {'python': ['xlwt']},
 'installable': True,
}
