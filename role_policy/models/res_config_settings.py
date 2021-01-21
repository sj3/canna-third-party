# Copyright (C) 2020 Simon Janssens (sj@startx.be).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    role_policy_enforced = fields.Boolean(
        string="Enforce role policy", config_parameter="role_policy_enforced"
    )
