# Copyright 2009-2025 Noviat
# Copyright 2025 Canna
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def copy(self, default=None):
        if self.env.context.get("account_invoice_split"):
            default = dict(default or {})
            default["line_ids"] = []
        return super().copy(default=default)

    def split_invoice(self):
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft invoices can be splitted"))

        if len(self.invoice_line_ids) < 2:
            raise UserError(_("At least two invoice lines required for a split"))

        view = self.env.ref("account_invoice_split.account_invoice_split_view_form")
        return {
            "name": _("Select Invoice Lines"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "account.invoice.split",
            "type": "ir.actions.act_window",
            "view": view.id,
            "target": "new",
            "context": dict(
                self.env.context,
                active_id=self.id,
                default_invoice_split_line_ids=self.invoice_line_ids.ids,
            ),
        }
