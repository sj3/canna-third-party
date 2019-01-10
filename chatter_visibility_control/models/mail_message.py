# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = 'mail.message'

    body_lang = fields.Char()

    @api.model
    def create(self, vals):
        vals['body_lang'] = self.env.user.lang
        return super(MailMessage, self).create(vals)

    @api.model
    def _message_read_dict(self, message, parent_id=False):
        msg_dict = super(MailMessage, self)._message_read_dict(
            message, parent_id=parent_id)
        chatter_control_models = safe_eval(
            self.env['ir.config_parameter']
            .get_param('chatter_visibility_control') or '[]')
        if msg_dict['model'] in chatter_control_models:
            msg_dict = self._message_control_visibility(message, msg_dict)
        return msg_dict

    def _message_control_visibility(self, message, msg_dict):
        model = self.env[message.model]

        removals = {}
        for name, field in model._fields.items():
            visibility = getattr(field, 'track_visibility', False)
            c1 = visibility in ['always', 'onchange'] or name in model._track
            c2 = (hasattr(field, 'track_visibility_groups') and not
                  self.env.user.user_has_groups(field.track_visibility_groups)
                  )
            if c1 and c2:
                removals[name] = field

        for f in removals:
            body_lang = message.body_lang or u'en_US'
            env = self.with_context({'lang': body_lang}).env
            field_string = removals[f].get_description(env)['string']
            for k in ['body', 'body_short']:
                body = msg_dict[k][:]
                if k == 'body':
                    replace_start = '<b>%s</b>: ' % field_string
                    replace_end = '</div>'
                else:
                    replace_start = '<b>%s</b><span>: ' % field_string
                    replace_end = '</span>'
                if replace_start in body:
                    i1 = body.find(replace_start) + len(replace_start)
                    i2 = i1 + msg_dict[k][i1:].find(replace_end)
                    msg_dict[k] = body[:i1] + _('changed') + body[i2:]
        return msg_dict
