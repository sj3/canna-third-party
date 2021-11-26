# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResCompany(models.Model):
    _inherit = "res.company"

    @api.model
    def get_mapbox_api_key(self):
        return self.env["ir.config_parameter"].sudo().get_param("mapbox.client_id")
