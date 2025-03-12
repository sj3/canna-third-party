# -*- coding: utf-8 -*-

from odoo import fields, models ,_
from odoo.exceptions import UserError


class AccountMoveSplit(models.TransientModel):
    _name = 'account.move.split'
    _description = 'Split Invoice'

    invoice_split_line_ids = fields.Many2many('account.move.line','account_move_split_move_line_rel',
        string='Invoice Lines')

    def split_invoice(self):
        """Split an invoice into two and update linked sales/purchase orders."""
        self.ensure_one()
        active_invoice_id = self._context.get("active_id")
        old_invoice = self.env["account.move"].browse(active_invoice_id)
        new_invoice = old_invoice.with_context(account_invoice_split=True).copy()
        lines_to_move = self.invoice_split_line_ids
        if lines_to_move:
            lines_to_move.with_context(check_move_validity=False).write({"move_id": new_invoice.id})
            for invoice in (old_invoice, new_invoice):
                invoice.with_context(check_move_validity=False)._recompute_dynamic_lines()
                if invoice.amount_total < 0:
                    raise UserError(_("The amount of the resulting invoices must be > 0."))
            order_models = ["sale.order", "purchase.order"]
            for model_name in order_models:
                if model_name in self.env.registry:
                    order_model = self.env[model_name]
                    orders = order_model.search([("invoice_ids", "in", old_invoice.ids)])
                    if orders:
                        orders.write({"invoice_ids": [(4, new_invoice.id)]})
            views = {
                "out_invoice": "account_move_action_customer",
                "out_refund": "account_move_action_customer_refund",
                "in_invoice": "account_move_action_supplier",
                "in_refund": "account_move_action_supplier_refund",
            }
            view = self.env.ref('canna_invoice.%s' % views.get(old_invoice.type))
            return {
                "name": _("Invoices"),
                "type": "ir.actions.act_window",
                "res_model": "account.move",
                "view_mode": "tree,form",
                "view": view.id,
                "target":"current",
                "domain": [("id", "in", (old_invoice + new_invoice).ids)],
            }
        else:
            raise UserError(_("Select At least one invoice line to split."))
