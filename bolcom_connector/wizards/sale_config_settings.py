# -*- coding: utf-8 -*-
# Copyright 2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "sale.config.settings"

    company_id = fields.Many2one(
        comodel_name="res.company", string="Company",
        default=lambda self: self.env.user.company_id)
    bolcom_client_id = fields.Char(
        related="company_id.bolcom_client_id",
        readonly=False,
        string="bol.com Client ID",
        help="Client ID from bol.com credentials",
    )
    bolcom_secret = fields.Char(
        related="company_id.bolcom_secret",
        readonly=False,
        string="bol.com Secret",
        help="Secret from bol.com credentials",
    )
    bolcom_url = fields.Char(
        related="company_id.bolcom_url", readonly=False, string="bol.com url",
    )
    bolcom_fiscal_position_id = fields.Many2one(
        comodel_name="account.fiscal.position",
        related="company_id.bolcom_fiscal_position_id",
        readonly=False, string="Fiscal Position",
    )

    @api.model
    def default_get(self, fields_list):
        res = super(SaleConfigSettings, self).default_get(fields_list)
        company = self.env.user.company_id
        if "company_id" in fields_list:
            res.update({"company_id": company.id})
        return res
