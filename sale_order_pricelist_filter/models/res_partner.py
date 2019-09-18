# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_pricelist_ids = fields.Many2many(
        string='Other Sale Pricelists',
        comodel_name='product.pricelist',
        relation='partner_sale_pricelist_rel',
        column1='partner_id',
        column2='pricelist_id',
        help="Specify here the list of pricelists that can be set on a "
             "Sale Order as an alternative to the standard 'Sale Pricelist'."
    )
