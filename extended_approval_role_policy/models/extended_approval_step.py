# Copyright 2021 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ExtendedApprovalStep(models.Model):
    _inherit = ["extended.approval.step"]

    role_ids = fields.Many2many(comodel_name="res.role", string="Approver")
    group_ids = fields.Many2many(compute="_compute_group_ids", store=True)

    @api.depends("role_ids")
    def _compute_group_ids(self):
        for rec in self:
            rec.group_ids = rec.role_ids.mapped('group_id')




