# -*- coding: utf-8 -*-
# Copyright (C) 2017 Onestein (http://www.onestein.eu/).
# Copyright (C) 2017 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid)
    )


class ProductPricelistVersion(models.Model):
    _inherit = 'product.pricelist.version'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        related='pricelist_id.operating_unit_id',
        string='Operating Unit',
        readonly=True)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        related='price_version_id.operating_unit_id',
        string='Operating Unit',
        readonly=True)
