# Copyright 2009-2018 Noviat.
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        compute="_compute_sale_order_count",
        string="Sale Orders",
    )
    sale_order_count = fields.Integer(
        compute="_compute_sale_order_count", string="# of Sales Order"
    )

    def _compute_sale_order_count(self):
        procs = self.env["procurement.group"].search([("purchase_id", "=", self.id)])
        self.sale_order_ids = procs.mapped("sale_id")
        self.sale_order_count = len(self.sale_order_ids)

    def view_sale_order(self):
        self.ensure_one()
        action = {}
        so_ids = [x.id for x in self.sale_order_ids]
        if so_ids:
            form = self.env.ref("sale.view_order_form")
            if len(so_ids) > 1:
                tree = self.env.ref("sale.view_order_tree")
                action.update(
                    {
                        "name": _("Sales Orders"),
                        "view_mode": "tree,form",
                        "views": [(tree.id, "tree"), (form.id, "form")],
                        "domain": [("id", "in", so_ids)],
                    }
                )
            else:
                action.update(
                    {
                        "name": _("Sales Order"),
                        "view_mode": "form",
                        "view_id": form.id,
                        "res_id": so_ids[0],
                    }
                )
            action.update(
                {
                    "context": self._context,
                    "view_type": "form",
                    "res_model": "sale.order",
                    "type": "ir.actions.act_window",
                }
            )
        return action
