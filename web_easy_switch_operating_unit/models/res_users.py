from odoo import models


class res_users(models.Model):
    _inherit = "res.users"

    def change_current_operating_unit(self, cr, uid, operating_unit_id, context=None):
        return self.write(cr, uid, uid, {"operating_unit": operating_unit_id})
