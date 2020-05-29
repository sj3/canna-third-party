# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockRule(models.Model):
    """Override PurchaseOrder for catalog prices."""

    _inherit = "stock.rule"

    def _prepare_purchase_order(self, company_id, origins, values):
        res = super()._prepare_purchase_order(company_id, origins, values)
        partner_id = res.get("partner_id", None)
        if partner_id is not None:
            partner = self.env["res.partner"].browse(partner_id)
            if partner.purchase_catalog_id:
                res["price_catalog_id"] = partner.purchase_catalog_id.id
        return res
