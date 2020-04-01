# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CrmVisitFeeling(models.Model):
    _name = "crm.visit.feeling"
    _description = "Visit feeling"

    name = fields.Char(string="Feeling", size=80, required=True, translate=True)
    active = fields.Boolean(default=True)
    # '_company_default_get' on res.company is deprecated and shouldn't be used
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
