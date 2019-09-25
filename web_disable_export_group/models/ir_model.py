# -*- coding: utf-8 -*-
# Copyright Onestein (https://www.onestein.eu/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openerp import fields, models


class IrModel(models.Model):
    _inherit = 'ir.model'

    export_group_ids = fields.Many2many(
        comodel_name='res.groups', relation='group_model_export_rel',
        column1='model_id', column2='group_id', string='Export Groups',
        help='Groups which are allowed to export records related to this'
        'model',
    )
