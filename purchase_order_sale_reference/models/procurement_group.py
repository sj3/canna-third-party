# Copyright 2009-2018 Noviat.
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProcurementGroup(models.Model):
    _inherit = "procurement.group"

    purchase_id = fields.Many2one(
        comodel_name="purchase.order", string="Purchase Order"
    )
