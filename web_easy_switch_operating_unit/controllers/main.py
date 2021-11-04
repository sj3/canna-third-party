import odoo
import odoo.http as http
from odoo.http import request


class WebEasySwitchOperatingUnitController(http.Controller):
    @http.route(
        "/web_easy_switch_operating_unit/switch/change_current_operating_unit",
        type="json",
        auth="none",
    )
    def change_current_operating_unit(self, operating_unit_id=False):
        registry = openerp.modules.registry.RegistryManager.get(request.session.db)
        uid = request.session.uid
        with registry.cursor() as cr:
            res = registry.get("res.users").change_current_operating_unit(
                cr, uid, operating_unit_id
            )
            return res
