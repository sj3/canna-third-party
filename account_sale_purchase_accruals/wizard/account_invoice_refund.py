# -*- coding: utf-8 -*-
# Copyright 2009-2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountInvoiceRefund(models.TransientModel):
    _inherit = 'account.invoice.refund'

    @api.multi
    def compute_refund(self, mode='refund'):
        """
        - handle accruals for refunds
        - maintain link with orig object when using option 'modify'
        - fix functional bug in Odoo: display draft invoice/refund
          when using option 'modify'
        """
        result = super(AccountInvoiceRefund, self).compute_refund(mode)

        orig_id = self.env.context.get('active_ids')
        if len(orig_id) != 1:
            module = __name__.split('addons.')[1].split('.')[0]
            raise UserError(_(
                "Error 001 detected in %s"
                "Please report this error via your Odoo "
                "support channel."
            ) % ', '.join([module, self._name]))
        orig_inv = self.env['account.invoice'].browse(orig_id)

        new_inv_ids = []
        domain = result['domain']
        for i, arg in enumerate(domain):
            if arg[0] == 'type' and mode == 'modify':
                domain[i] = ('type', '=', orig_inv.type)
            if arg[0] == 'id' and arg[1] == 'in':
                new_inv_ids = arg[2]

        if mode == 'modify':
            xml_id = {
                'out_invoice': 'action_invoice_tree1',
                'out_refund': 'action_invoice_tree3',
                'in_invoice': 'action_invoice_tree2',
                'in_refund': 'action_invoice_tree4',
            }[orig_inv.type]
            result = self.env['ir.actions.act_window'].for_xml_id(
                'account', xml_id)
            result['domain'] = domain

        for new_inv in self.env['account.invoice'].browse(new_inv_ids):
            if new_inv.type == orig_inv.type:
                new_inv.origin = orig_inv.origin

            # restore link to origin SO/PO
            if new_inv.type == 'out_invoice':
                new_inv.sale_order_ids = orig_inv.sale_order_ids
                new_lines = new_inv.invoice_line
                for i, line in enumerate(orig_inv.invoice_line):
                    if new_lines[i].product_id != line.product_id:
                        raise UserError(_(
                            "Error 002 detected in %s"
                            "Please report this error via your Odoo "
                            "support channel."
                        ) % ', '.join([module, self._name]))
                    new_lines[i].sale_order_line_ids = \
                        line.sale_order_line_ids
            elif new_inv.type == 'in_invoice':
                new_inv.purchase_order_ids = orig_inv.purchase_order_ids

        return result
