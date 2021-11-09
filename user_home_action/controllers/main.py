# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging
_logger = logging.getLogger(__name__)

class HomeActionMenuForLoginUser(http.Controller):
    @http.route('/set_user_home_action', type='json', auth="user")
    def set_user_home_action(self, **kwargs):
        """Set current action to user's home action."""
        request.env.user.sudo().write({'action_id': int(kwargs.get('actionID'))})
        return True
