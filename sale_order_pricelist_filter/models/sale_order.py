# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    allowed_pricelist_ids = fields.Many2many(
        comodel_name='product.pricelist',
        compute='_compute_allowed_pricelist_ids',
    )

    @api.depends('partner_id.commercial_partner_id.property_product_pricelist',
                 'partner_id.commercial_partner_id.sale_pricelist_ids')
    def _compute_allowed_pricelist_ids(self):
            cp = self.partner_id.commercial_partner_id
            self.allowed_pricelist_ids = cp.property_product_pricelist \
                + cp.sale_pricelist_ids
