# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class HiddenTemplateField(models.Model):
    _name = 'web.hidden.template.field'
    _description = 'Hidden template field'
    _order = 'sequence'

    sequence = fields.Integer(default=100)

    name = fields.Many2one(
        comodel_name='ir.model.fields',
        string='Field',
        required=True)

    users = fields.Many2many(
        comodel_name='res.users',
        string='Users',
        relation='web_hidden_field_user',
        column1='hidden_field',
        column2='hidden_user',
        help="If you don't select any user, the field is hidden for all users")

    groups = fields.Many2many(
        comodel_name='res.groups',
        string='Groups',
        relation='web_hidden_field_group',
        column1='hidden_field',
        column2='hidden_group',
        help="If you don't select any group, the field"
        "is hidden for all groups")

    expression = fields.Text()

    active = fields.Boolean(
        related='template_id.active')

    model = fields.Many2one(
        comodel_name='ir.model',
        related='template_id.name')

    company_id = fields.Many2one(
        comodel_name='res.company',
        related='template_id.company_id')

    template_id = fields.Many2one(
        comodel_name='web.hidden.template',
        ondelete='cascade')

    hidden = fields.Boolean(
        string="Field hidden?")
