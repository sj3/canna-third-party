# Copyright (C) 2021-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).

from odoo import fields, models


class ExtendedApprovalHistory(models.Model):
    _inherit = "extended.approval.history"

    source = fields.Reference(selection_add=[("sales.target", "Sale Target")])
