# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import logging

from openerp import api, fields, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    bolcom_order_item_ref = fields.Char()
    bolcom_offer_ref = fields.Char()
    bolcom_transaction_fee = fields.Float()

    def _bolcom_sale_order_line_mapping(self):
        return {
            "orderItemId": {"field": "bolcom_order_item_ref"},
            "offerReference": {"ignore": True},
            "ean": {"method": "_bolcom_handle_ean"},
            "title": {"ignore": True},
            "quantity": {"method": "_bolcom_handle_qt_price"},
            "offerPrice": {"method": "_bolcom_handle_qt_price"},
            "offerId": {"field": "bolcom_offer_ref"},
            "transactionFee": {"field": "bolcom_transaction_fee"},
            "exactDeliveryDate": {"ignore": True},
            "latestDeliveryDate": {"ignore": True},
            "expiryDate": {"ignore": True},
            "offerCondition": {"ignore": True},
            "cancelRequest": {"ignore": True},
            "fulfilmentMethod": {"ignore": True},
        }

    def _bolcom_handle_ean(self, key, order_item, vals):
        name_fields = ["ean"]
        product_ids = self.env["product.product"].search(
            [("ean13", "=", order_item.get("ean"))]
        )
        product_id = False
        if len(product_ids) > 0:
            product_id = product_ids[0]
            vals["product_id"] = product_id.id
        if not product_ids:
            _logger.error(
                "No corresponding product found for orderItem %s",
                order_item
            )
        elif len(product_ids) > 1:
            _logger.error(
                "Multiple product records found ean %s",
                order_item.get("ean")
            )
        return name_fields

    def _bolcom_handle_qt_price(self, key, order_item, vals):
        name_fields = ["quantity", "offerPrice"]
        vals["product_uom_qty"] = order_item["quantity"]
        vals["price_unit"] = order_item["offerPrice"]
        return name_fields

    @api.model
    def _prepare_order_line_invoice_line(self, line, account_id=False):
        vals = super(SaleOrderLine, self)._prepare_order_line_invoice_line(
            line, account_id=account_id)
        vals["bolcom_transaction_fee"] = line.bolcom_transaction_fee
        return vals

    @api.multi
    def _bolcom_get_order_line_vals(self, sale_order, order_item):
        mapping_specs = self._bolcom_sale_order_line_mapping()
        handled = []
        vals = {}
        for key, value in order_item.items():
            if key in handled:
                continue
            mapping = mapping_specs.get(key)
            if not mapping:
                _logger.error("Missing mapping table entry for parameter %s", key)
            else:
                if mapping.get("ignore"):
                    handled.append(key)
                    continue
                if mapping.get("method"):
                    method = "{}".format(mapping_specs[key]["method"])
                    handled.extend(getattr(self, method)(key, order_item, vals))
                else:
                    vals[mapping["field"]] = value
                    handled.append(key)

        # ../.. sale_order.fiscal_position is set to false => bug
        extra_vals = self.product_id_change(
            sale_order.pricelist_id.id,
            vals['product_id'],
            qty=vals["product_uom_qty"],
            partner_id=sale_order.partner_id.id,
            date_order=sale_order.date_order,
            fiscal_position=sale_order.fiscal_position.id
        ).get("value", {})
        if extra_vals.get('tax_id'):
            extra_vals['tax_id'] = [(6, 0, extra_vals['tax_id'])]
        vals.update({k: v for k, v in extra_vals.items() if k not in vals})
        return vals
