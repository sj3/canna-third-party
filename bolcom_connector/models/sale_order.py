# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    bolcom_order_ref = fields.Char()

    def _bolcom_sale_order_mapping(self):
        return {
            "orderId": {"field": "bolcom_order_ref"},
            "pickUpPoint": {"ignore": True},
            "dateTimeOrderPlaced": {"field": "date_order"},
            "customerDetails": {"method": "_bolcom_handle_partners"},
            # ignore orderItems since handled after SO create
            "orderItems": {"ignore": True},
        }

    @api.model
    def import_bolcom_order(self, action=None):
        sale_orders = self.browse()
        BolcomAuthentication = self.env["bolcom.authentication"].sudo()
        # request to bolcom
        token = BolcomAuthentication.get_token()
        bolcom_orders = BolcomAuthentication.request_resource(
            token, "orders", query="fulfilment-method=FBR"
        )
        for bolcom_order in bolcom_orders.get("orders", {}):
            bol_order_vals = BolcomAuthentication.request_resource(
                token, "orders", id=bolcom_order.get("orderId")
            )
            if not bol_order_vals:
                _logger.error("No order_vals for bolcom_order %s", bolcom_order)
                continue
            sale_order = self.search(
                [("bolcom_order_ref", "=", bol_order_vals["orderId"])]
            )
            if sale_order:
                _logger.warning(
                    "Existing sale order for bolcom order %s - %s",
                    sale_order.name,
                    sale_order.bolcom_order_ref,
                )
                continue

            order_items = self._filter_order_items(bol_order_vals)
            if not order_items:
                _logger.error(
                    "No order lines for bolcom_order %s",
                    bolcom_order)
                continue

            mapping_specs = self._bolcom_sale_order_mapping()
            sale_order = self._bolcom_order_to_sale_order(
                bol_order_vals, mapping_specs)
            if sale_order:
                sale_order._bolcom_create_sale_order_lines(order_items)
                sale_orders += sale_order

        if action in ["confirm", "invoice"]:
            for so in sale_orders:
                so.action_button_confirm()
            if action == "invoice":
                sale_orders.action_invoice_create()
                # TODO: add invoice validate
        return sale_orders

    @api.multi
    def _bolcom_order_to_sale_order(self, bol_order_vals, mapping_specification):
        handled = []
        vals = {}
        for key, value in bol_order_vals.items():
            if key in handled:
                continue
            mapping = mapping_specification.get(key)
            if not mapping:
                _logger.error("Missing mapping table entry for parameter %s", key)
            else:
                if mapping.get("ignore"):
                    handled.append(key)
                    continue
                if mapping.get("method"):
                    method = "{}".format(mapping_specification[key]["method"])
                    handled.extend(getattr(self, method)(key, bol_order_vals, vals))
                else:
                    vals[mapping["field"]] = value
                    handled.append(key)

        extra_vals = self.onchange_partner_id(vals["partner_id"]).get("value", {})
        vals.update({k: v for k, v in extra_vals.items() if k not in vals})
        return self.create(vals)

    def _filter_order_items(self, bol_order_vals):
        order_items = []
        for entry in bol_order_vals.get("orderItems", []):
            if entry.get("cancelRequest"):
                _logger.warning(
                    "Bolcom order contains cancelRequest for order line %s - %s",
                    bol_order_vals["orderId"],
                    bol_order_vals["orderItemId"]
                )
            else:
                order_items.append(entry)
        return order_items

    def _bolcom_handle_partners(self, key, bol_order_vals, vals):
        name_fields = ["customerDetails"]
        ResPartner = self.env["res.partner"]
        customer_details = bol_order_vals.get("customerDetails", {})
        # billing_details = customer_details.get('billingDetails', {}) # V13
        shipment_details = customer_details.get("shipmentDetails")
        if not shipment_details:
            _logger.error("No shipment adres found for in %s", bol_order_vals)
            return name_fields
        shipment_partners = ResPartner.search(
            [
                ("email", "=", shipment_details.get("email", False)),
                ("bolcom_customer", "=", True),
                ("type", "=", "delivery"),
            ]
        )
        shipment_partner = shipment_partners or ResPartner
        shipment_partner = shipment_partner.bolcom_synchronize(shipment_details)
        vals["partner_id"] = shipment_partner.id
        return name_fields

    def _bolcom_create_sale_order_lines(self, order_items):
        self.ensure_one()
        sol_obj = self.env['sale.order.line']
        line_vals = []
        for order_item in order_items:
            line_vals.append(
                sol_obj._bolcom_get_order_line_vals(self, order_item)
            )
        self.write({'order_line': [(0, 0, x) for x in line_vals]})
