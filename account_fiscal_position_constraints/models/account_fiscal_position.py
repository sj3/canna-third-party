# Copyright 2009-2024 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models
from odoo.exceptions import RedirectWarning


class AccountFiscalPosition(models.Model):
    _inherit = "account.fiscal.position"

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique (name, company_id)",
            "The name of the fiscal position must be unique per company !",
        )
    ]

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {})
        default.setdefault("name", _("%s (copy)") % (self.name or ""))
        return super().copy(default)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_linked_to_partner_or_invoice(self):
        for fpos in self:
            partner_count = (
                self.env["res.partner"]
                .with_context(active_test=False)
                .search_count([("property_account_position_id", "=", fpos.id)], limit=1)
            )
            if partner_count:
                action = self.env.ref("base.action_partner_form").id

                raise RedirectWarning(
                    _(
                        "You cannot delete a fiscal position that "
                        "has been set on partner records"
                        "\nAs an alternative, you can disable a "
                        "fiscal position with the button 'Archive'"
                    ),
                    action,
                    _("View partners"),
                    additional_context={
                        "search_default_property_account_position_id": fpos.id
                    },
                )

            move_count = (
                self.env["account.move"]
                .with_context(active_test=False)
                .search_count([("fiscal_position_id", "=", fpos.id)], limit=1)
            )
            if move_count:
                action = self.env.ref("account.action_move_journal_line").id
                raise RedirectWarning(
                    _(
                        "You cannot delete a fiscal position that "
                        "has been set on partner records"
                        "\nAs an alternative, you can disable a "
                        "fiscal position with the button 'Archive'"
                    ),
                    action,
                    _("View invoices"),
                    additional_context={"search_default_fiscal_position_id": fpos.id},
                )
