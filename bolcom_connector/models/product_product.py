# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

''' not used in 8.0 version of this module

from openerp import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_bolcom = fields.Boolean(string="Sellable on bol.com")
    to_bolcom = fields.Boolean(
        string="Transferable to bol.com",
        help="Indicates that the product must be created or updated on bol.com"
    )
    bolcom_offer_ref = fields.Char()
    bolcom_condition_name = fields.Char()
    bolcom_condition_category = fields.Char()
    bolcom_condition_comment = fields.Char()
    bolcom_bundle_prices_price = fields.Char()
    bolcom_fulfilment_delivery_code = fields.Char()
    bolcom_on_hold_by_retailer = fields.Char()
    bolcom_fulfilment_type = fields.Char()
    bolcom_reference_code = fields.Char()
    bolcom_stock_amount = fields.Float()

    def set_bolcom_sellable(self):
        """
        Sets the product to be sellable on bol.com and marks it as transferable
        """
        for rec in self:
            if not rec.is_bolcom:
                rec.write({'is_bolcom': True, 'to_bolcom': True})
        return

    def unset_bolcom_sellable(self):
        """
        Sets the product to be not sellable on bol.com and marks it as transferable
        """
        for rec in self:
            if rec.is_bolcom:
                rec.write({'is_bolcom': False, 'to_bolcom': True})
        return
'''
