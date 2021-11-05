from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        info = super().session_info()

        if self.env.user.has_group("base.group_user"):
            user = request.env.user
            info.update(
                {
                    "user_operating_units": {
                        "current_operating_unit": (
                            user.default_operating_unit_id.id,
                            user.default_operating_unit_id.name,
                        ),
                        "allowed_operating_units": [
                            (ou.id, ou.name) for ou in user.operating_unit_ids
                        ],
                    }
                }
            )

        return info
