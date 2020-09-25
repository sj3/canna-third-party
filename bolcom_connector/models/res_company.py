# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    bolcom_client_id = fields.Char(
        string="bol.com Client ID", help="Client ID from bol.com credentials",
    )
    bolcom_secret = fields.Char(
        string="bol.com Secret", help="Secret from bol.com credentials",
    )
    bolcom_url = fields.Char(string="bol.com url")
    bolcom_fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        string="Fiscal Position",
        help="Default Fiscal Position for bol.com Customers."
    )

    @api.multi
    def write(self, vals):
        """
        strip blanks that may result from cut & paste
        """
        for f in ["bolcom_client_id", "bolcom_secret", "bolcom_url"]:
            if vals.get(f):
                vals[f] = vals[f].strip()
        return super(ResCompany, self).write(vals)
