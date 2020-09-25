# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import _, api, fields, models

_logger = logging.getLogger(__name__)


class BolcomSoImport(models.TransientModel):
    _name = "bolcom.so.import"
    _description = "Import SO from Bolcom"

    action = fields.Selection(
        selection=[
            ("draft", "Create Draft Orders"),
            ("confirm", "Confirm Orders"),
            ("invoice", "Confirm & Invoice Orders")
        ],
        default="invoice",
    )
    note = fields.Text(string="Log")

    @api.multi
    def import_bolcom_order(self):
        orders = self.env["sale.order"].import_bolcom_order(action=self.action)
        self.note = "{} new sale orders".format(len(orders))
        module = __name__.split("addons.")[1].split(".")[0]
        result_view = self.env.ref("%s.bolcom_so_import_view_form_result" % module)
        return {
            "name": _("Import orders from bol.com result"),
            "res_id": self.id,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "bolcom.so.import",
            "view_id": result_view.id,
            "target": "new",
            "context": dict(self.env.context, sale_order_ids=orders.ids),
            "type": "ir.actions.act_window",
        }

    @api.multi
    def view_sale_orders(self):
        self.ensure_one()
        action = {}
        so_ids = self.env.context.get("sale_order_ids", [])
        form = self.env.ref("sale.view_order_form")
        if len(so_ids) > 1:
            tree = self.env.ref("sale.view_order_tree")
            action.update({
                "name": _("bol.com Sales Orders"),
                "view_mode": "tree,form",
                "views": [(tree.id, "tree"), (form.id, "form")],
                "domain": [("id", "in", so_ids)],
            })
        elif len(so_ids) == 1:
            action.update({
                "name": _("bol.com Sales Order"),
                "view_mode": "form",
                "view_id": form.id,
                "res_id": so_ids[0],
            })
        else:
            return {"type": "ir.actions.act_window_close"}
        action.update({
            "context": self.env.context,
            "view_type": "form",
            "res_model": "sale.order",
            "type": "ir.actions.act_window",
        })
        return action
