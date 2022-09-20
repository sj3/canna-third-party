# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class AccountFinancialAbstractReport(models.AbstractModel):
    _inherit = "report.account_financial_report.abstract_report"

    @api.model
    def _get_move_lines_domain_not_reconciled(self, *args, **kwargs):
        domain = super()._get_move_lines_domain_not_reconciled(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain

    @api.model
    def _get_new_move_lines_domain(self, *args, **kwargs):
        domain = super()._get_new_move_lines_domain(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain
