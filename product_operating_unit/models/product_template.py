# -*- coding: utf-8 -*-
# Copyright (C) 2017 Onestein (http://www.onestein.eu/).
# Copyright (C) 2017 Noviat nv/sa (www.noviat.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
    )
