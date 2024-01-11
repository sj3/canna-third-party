# Copyright 2009-2023 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def write(self, vals):
        recs = self
        if {x for x in vals} == {"res_id", "res_model"}:
            recs = recs.filtered(
                lambda rec: not self.search_count([
                    ("res_id", "=", vals["res_id"]),
                    ("res_model", "=", vals["res_model"]),
                    ("checksum", "=", rec.checksum),
                ])
            )
            if not len(recs):
                return True

        return super(IrAttachment, recs).write(vals)
