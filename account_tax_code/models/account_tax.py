# Copyright 2009-2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    code = fields.Char()

    _sql_constraints = [
        (
            "code_company_uniq",
            "unique (code,company_id)",
            "The code of the Tax must be unique per company !",
        )
    ]

    def _compute_display_name(self):
        if self.env.context.get("append_code_to_tax_name"):
            for rec in self:
                rec.display_name = (rec.code and f"[{rec.code}]" or "") + f"{rec.name}"
        else:
            for rec in self:
                rec.display_name = rec.name

    def copy_data(self, default=None):
        default = dict(default or {})
        vals_list = super().copy_data(default=default)
        for tax, vals in zip(self, vals_list, strict=True):
            if tax.code:
                vals["code"] = _("%s (Copy)", tax.code)
        return vals_list
