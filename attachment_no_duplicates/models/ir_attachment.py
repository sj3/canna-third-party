# Copyright 2009-2023 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def write(self, vals):
        if {x for x in vals} == {"res_id", "res_model"}:
            dom = [
                ("res_id", "=", vals["res_id"]),
                ("res_model", "=", vals["res_model"]),
                ("checksum", "=", self.checksum),
            ]
            if self._search(dom):
                return True
        return super().write(vals)
