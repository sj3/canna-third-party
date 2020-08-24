# -*- coding: utf-8 -*-
from openerp import api, models


class AccountInvoice(models.Model):
    _name = 'account.invoice'
    _inherit = ['account.invoice', 'extended.approval.workflow.mixin']

    workflow_signal = 'invoice_open'
    workflow_state = 'extended_approval'

    @api.multi
    def action_cancel(self):
        self.cancel_approval()
        return super(AccountInvoice, self).action_cancel()

    @api.multi
    def approve_step(self):
        """
        Validate taxes before entering approval, not only on last step.
        """
        self.ensure_one()
        if self.state == 'draft':
            compute_taxes = self.env['account.invoice.tax'].compute(
                self.with_context(lang=self.partner_id.lang))
            self.check_tax_lines(compute_taxes)

        return super(AccountInvoice, self).approve_step()
