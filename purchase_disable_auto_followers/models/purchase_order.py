# Copyright 2009-2016 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def create(self, vals):
        res = super(PurchaseOrder, self).create(vals)
        partner_ids = self.env["res.partner"].search(
            [("id", "child_of", self.env.user.partner_id.commercial_partner_id.id)]
        )
        res.message_unsubscribe(partner_ids=partner_ids.ids)
        return res
