# -*- coding: utf-8 -*-
# Copyright Onestein (https://www.onestein.eu/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openerp import fields, models


class ResGroups(models.Model):
    _inherit = 'res.groups'

    export_model_ids = fields.Many2many(
        comodel_name='ir.model', relation='group_model_export_rel',
        column1='group_id', column2='model_id', string='Exportable Models',
        help='Models of which this group is allowed to export records of.'
    )
