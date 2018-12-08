# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import models, fields


class HiddenTemplateElement(models.Model):
    _name = 'web.hidden.template.element'
    _description = 'Hidden template element'
    _order = 'sequence'

    sequence = fields.Integer(default=100)

    element_type = fields.Selection(
        string="Element type",
        selection=[
            ('button', 'Button'),
            ('page', 'Page'),
        ],
        default='button',
        required=True)

    name = fields.Char(
        string='Element name',
        size=256,
        required=True)

    users = fields.Many2many(
        comodel_name='res.users',
        string='Users',
        relation='web_hidden_element_user',
        column1='hidden_element',
        column2='hidden_user',
        help="If you don't select any user, the element"
        " is hidden for all users")

    groups = fields.Many2many(
        comodel_name='res.groups',
        string='Groups',
        relation='web_hidden_element_group',
        column1='hidden_element',
        column2='hidden_group',
        help="If you don't select any group, the element"
        " is hidden for all groups")

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
