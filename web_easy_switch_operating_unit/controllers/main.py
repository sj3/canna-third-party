import odoo.http as http
from odoo.http import request


class WebEasySwitchOperatingUnitController(http.Controller):
    @http.route(
        "/web_easy_switch_operating_unit/switch/change_current_operating_unit",
        type="json",
        auth="user",
    )
    def change_current_operating_unit(self, operating_unit_id=False):
        request.env.user.write({"default_operating_unit_id": operating_unit_id})
