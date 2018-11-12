# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class HiddenTemplate(models.Model):
    _name = 'hidden.template'
    _description = 'Hidden template'

    def _default_company(self):
        return self.env['res.company']._company_default_get('hidden.template')

    name = fields.Many2one(
        comodel_name='ir.model',
        string='Model',
        required=True)

    active = fields.Boolean(
        string="Active",
        default=True)

    hidden_fields = fields.One2many(
        comodel_name='hidden.template.field',
        inverse_name='template_id')

    hidden_elements = fields.One2many(
        comodel_name='hidden.template.element',
        inverse_name='template_id')

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        index=True,
        required=True,
        default=_default_company)
