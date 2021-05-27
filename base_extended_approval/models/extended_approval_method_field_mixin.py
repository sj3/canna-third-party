# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ExtendedApprovalMethodFieldMixin(models.AbstractModel):
    """
    This mixin will trigger the extended approval on the call
    of the named method.
    """

    _name = "extended.approval.method.field.mixin"
    _inherit = ["extended.approval.state_field.mixin", "extended.approval.method.mixin"]
    _description = "Mixin class for extended approval button with field"
