# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models


class PartnerBalanceWizard(models.TransientModel):
    _inherit = 'partner.balance.webkit'

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)

    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}
        if context.get('xls_export'):
            # we update form with display account value
            data = self.pre_print_report(cr, uid, ids, data, context=context)
            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'account.account_report_partner_balance_xls',
                'datas': data}
        else:
            return super(PartnerBalanceWizard, self)._print_report(
                cr, uid, ids, data, context=context)
