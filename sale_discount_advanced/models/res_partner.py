# Copyright (C) 2016-2022 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="partner_sale_discount_rel",
        column1="partner_id",
        column2="discount_id",
        string="Sale Discounts",
    )
