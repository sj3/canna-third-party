# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY Serpent Consulting Services Pvt. Ltd.
#    (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class CrmPartnerAction(models.Model):
    _inherit = "crm.partner.action"

    operating_unit_id = fields.Many2one(
        "operating.unit",
        "Operating Unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(
            self._uid
        ),
    )
