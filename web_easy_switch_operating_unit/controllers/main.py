# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 ICTSTUDIO (<http://www.ictstudio.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import openerp
import openerp.http as http
from openerp.http import request


class WebEasySwitchOperatingUnitController(http.Controller):
    @http.route(
        '/web_easy_switch_operating_unit/switch/change_current_operating_unit',
        type='json', auth='none')
    def change_current_operating_unit(self, operating_unit_id=False):
        registry = openerp.modules.registry.RegistryManager.get(
            request.session.db)
        uid = request.session.uid
        with registry.cursor() as cr:
            res = registry.get("res.users").change_current_operating_unit(
                cr, uid, operating_unit_id)
            return res
