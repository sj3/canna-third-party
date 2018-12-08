# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
from openerp import api, models

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.multi
    def _check_web_hidden_field(self, model_name, field_name):
        model = self.env['ir.model'].search(
            [('model', '=', model_name)], limit=1)
        if not model:
            _logger.error("Model '%s' not found!", model_name)
            return False

        field = self.env['ir.model.fields'].search(
            [('name', '=', field_name), ('model_id', '=', model.id)], limit=1)
        if not field:
            return False

        hidden_fields = self.env['web.hidden.template.field'].search(
            [('name', '=', field.id),
             ('model', '=', model.id),
             ('company_id', '=', self.env.user.company_id.id),
             ('active', '=', True)])

        for hidden_field in hidden_fields:

            if not hidden_field.users and not hidden_field.groups:
                # default rule
                return hidden_field

            if self.env.user in hidden_field.users:
                return hidden_field

            for group in hidden_field.groups:
                if group in self.env.user.groups_id:
                    return hidden_field

        return False

    @api.multi
    def _check_web_hidden_element(self, model_name, node):
        model = self.env['ir.model'].search(
            [('model', '=', model_name)], limit=1)

        if not model:
            _logger.error("Model '%s' not found!", model_name)
            return False

        hidden_fields = self.env['web.hidden.template.element'].search(
            [('name', '=', node.get('name')),
             ('element_type', '=', node.tag),
             ('model', '=', model.id),
             ('company_id', '=', self.env.user.company_id.id),
             ('active', '=', True)])

        for hidden_field in hidden_fields:

            if not hidden_field.users and not hidden_field.groups:
                # default rule
                return hidden_field

            if self.env.user in hidden_field.users:
                return hidden_field

            for group in hidden_field.groups:
                if group in self.env.user.groups_id:
                    return hidden_field

        return False

    @api.model
    def postprocess(self, model, node, view_id, in_tree_view, model_fields):
        if node.tag == 'field':
            hidden_field = self._check_web_hidden_field(
                    model, node.get('name'))
            if hidden_field:
                expr = ('True' if hidden_field.expression is False else
                        hidden_field.expression)
                # Must be hidden apply the group to the field
                if expr.lower() == 'true' and hidden_field.hidden:
                    if node.get('sum'):
                        node.attrib.pop('sum')
                    node.set(
                        'groups',
                        'web_hidden_element.group_hidden_fields_no_one')
                # Apply expression
                node.set('invisible_expression', expr)
                node.set('hidden', unicode(hidden_field.hidden))
        elif node.tag in ['button', 'page'] and node.get('name'):
            hidden_element = self._check_web_hidden_element(model, node)
            if hidden_element:
                expr = ('True' if hidden_element.expression is False else
                        hidden_element.expression)
                if expr.lower() == 'true' and hidden_element.hidden:
                    node.set(
                        'groups',
                        'web_hidden_element.group_hidden_fields_no_one')
                # Apply expression
                node.set('invisible_expression', expr)
                node.set('hidden', unicode(hidden_element.hidden))

        fields = super(IrUiView, self).postprocess(
            model, node, view_id, in_tree_view, model_fields)
        return fields
