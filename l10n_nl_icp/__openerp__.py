# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Netherlands - ICP Report',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Noviat",
    'website': 'http://www.noviat.com',
    'category': 'Localization',
    'depends': [
        'account',
        'report_xlsx_helpers',
    ],
    'data': [
        'views/l10n_nl_layouts.xml',
        'views/report_l10n_nl_vat_intracom.xml',
        'wizards/accounting_report.xml',
        'wizards/l10n_nl_vat_common.xml',
        'wizards/l10n_nl_vat_intracom.xml',
    ],
    'installable': True,
}
