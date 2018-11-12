# -*- coding: utf-8 -*-
# Copyright 2017 Ignacio Ibeas <ignacio@acysos.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json
import logging


from openerp import api, models, SUPERUSER_ID
from openerp.osv import orm

_logger = logging.getLogger(__name__)


class IrUiView(models.Model):
    _inherit = 'ir.ui.view'

    @api.multi
    def _check_hidden_field(self, model_name, field_name):
        model = self.env['ir.model'].search(
            [('model', '=', model_name)], limit=1)
        if not model:
            _logger.error("Model '%s' not found!", model_name)
            return False

        field = self.env['ir.model.fields'].search(
            [('name', '=', field_name), ('model_id', '=', model.id)], limit=1)
        if not field:
            # _logger.error("Field '%s' not found on model '%s'!",
            #               field_name, model_name)
            return False

        hidden_fields = self.env['hidden.template.field'].search(
            [('name', '=', field.id),
             ('model', '=', model.id),
             ('company_id', '=', self.env.user.company_id.id),
             ('active', '=', True)])

        for hidden_field in hidden_fields:

            if not hidden_field.users and not hidden_field.groups:
                # default rule
                return hidden_field.hidden

            if self.env.user in hidden_field.users:
                return hidden_field.hidden

            for group in hidden_field.groups:
                if group in self.env.user.groups_id:
                    return hidden_field.hidden

        return False

    @api.multi
    def _check_hidden_element(self, model_name, node):
        model = self.env['ir.model'].search(
            [('model', '=', model_name)], limit=1)

        if not model:
            _logger.error("Model '%s' not found!", model_name)
            return False

        hidden_fields = self.env['hidden.template.element'].search(
            [('name', '=', node.get('name')),
             ('model', '=', model.id),
             ('company_id', '=', self.env.user.company_id.id),
             ('active', '=', True)])

        for hidden_field in hidden_fields:

            if not hidden_field.users and not hidden_field.groups:
                # default rule
                return hidden_field.hidden

            if self.env.user in hidden_field.users:
                return hidden_field.hidden

            for group in hidden_field.groups:
                if group in self.env.user.groups_id:
                    return hidden_field.hidden

        return False

    @api.model
    def postprocess(self, model, node, view_id, in_tree_view, model_fields):
        if self._uid != SUPERUSER_ID:
            if node.tag == 'field':
                if self._check_hidden_field(model, node.get('name')):
                    if node.get('sum'):
                        node.attrib.pop('sum')
                    node.set(
                        'groups',
                        'web_hidden_element.group_hidden_fields_no_one')
            if node.tag in ['button', 'page'] and node.get('name'):
                if self._check_hidden_element(model, node):
                    node.set(
                        'groups',
                        'web_hidden_element.group_hidden_fields_no_one')

        fields = super(IrUiView, self).postprocess(
            model, node, view_id, in_tree_view, model_fields)
        return fields
