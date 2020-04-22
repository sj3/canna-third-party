# Copyright 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    purchase_order_ids = fields.Many2many(
        comodel_name="purchase.order",
        compute="_compute_purchase_order_ids",
        search="_search_purchase_order_ids",
        string="Purchase Orders",
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_ids", string="# of Sales Order"
    )

    def _compute_purchase_order_ids(self):
        procs = self.env["procurement.group"].search([("sale_id", "=", self.id),])
        self.purchase_order_ids = procs.mapped("purchase_id")
        self.purchase_order_count = len(self.purchase_order_ids)

    @api.model
    def _search_purchase_order_ids(self, operator, value):
        if operator == "in":
            if isinstance(value, int):
                value = [value]
            so_ids = (
                self.env["procurement.group"]
                .search([("purchase_id", "in", value)])
                .mapped("sale_id.id")
            )
            return [("id", "in", so_ids)]
        else:
            raise Warning(_("Unsupported operand for search!"))

    def view_purchase_order(self):
        self.ensure_one()
        action = self.env.ref(
            "sale_order_purchase_reference.purchase_order_action_sales"
        ).read()[0]
        po_ids = [x.id for x in self.purchase_order_ids]
        if po_ids:
            action.update(
                {"domain": [("id", "in", po_ids)],}
            )
            if len(po_ids) == 1:
                action.update(
                    {
                        "views": [v for v in action.get("views", []) if v[1] == "form"],
                        "res_id": po_ids[0],
                    }
                )

        return action
