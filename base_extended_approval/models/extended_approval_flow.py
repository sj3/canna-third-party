# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .extended_approval_mixin import ExtendedApprovalMixin


class ExtendedApprovalFlow(models.Model):
    _name = "extended.approval.flow"
    _inherit = ["extended.approval.config.mixin"]
    _description = "Extended approval flow"
    _order = "sequence"

    name = fields.Char(string="Name")
    sequence = fields.Integer(string="Priority", default=10)
    model = fields.Selection(
        string="Model name", selection="_get_extended_approval_models"
    )
    domain = fields.Char(string="Domain for this flow")
    steps = fields.One2many(
        comodel_name="extended.approval.step", inverse_name="flow_id", string="Steps"
    )

    def get_applicable_models(self):
        return [self.model]

    @api.model
    def _get_extended_approval_models(self):
        def _get_subclasses(cls):
            for sc in cls.__subclasses__():
                for ssc in _get_subclasses(sc):
                    yield ssc
                yield sc

        return [
            (x, x)
            for x in list(
                {
                    c._name
                    for c in _get_subclasses(ExtendedApprovalMixin)
                    if issubclass(c, models.Model) and hasattr(c, "_name")
                }
            )
        ]
