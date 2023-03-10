# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ExtendedApprovalStep(models.Model):
    _name = "extended.approval.step"
    _inherit = ["extended.approval.config.mixin"]
    _description = "Extended approval step"
    _order = "sequence"

    flow_id = fields.Many2one(
        comodel_name="extended.approval.flow", string="Extended Approval", required=True
    )

    sequence = fields.Integer(string="Priority", default=10)

    condition = fields.Many2one(
        comodel_name="extended.approval.condition", string="Condition"
    )

    group_ids = fields.Many2many(comodel_name="res.groups", string="Approver")

    use_sudo = fields.Boolean(
        string="Approver (sudo)",
        help="The actual approval will be done by the last user "
        "in the approval history with this flag set.",
    )

    def get_applicable_models(self):
        return [self.flow_id.model]

    def is_applicable(self, record):
        return self.condition.is_applicable(record) if self.condition else True
