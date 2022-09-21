# Copyright 2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PriceSubcatalog(models.Model):
    _inherit = "price.subcatalog"

    operating_unit_id = fields.Many2one(
        comodel_name="operating.unit",
        default=lambda self: self.env["res.users"].operating_unit_default_get(),
    )

    def action_duplicate_subcatalog(self):
        res = super(PriceSubcatalog, self).action_duplicate_subcatalog()
        if res.get('context'):
            res['context'].update({'default_operating_unit_id': self.operating_unit_id.id})
        return res
