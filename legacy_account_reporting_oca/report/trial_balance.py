# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class TrialBalanceReport(models.AbstractModel):
    _inherit = "report.account_financial_report.trial_balance"

    def _get_initial_balances_bs_ml_domain(self, *args, **kwargs):
        domain = super()._get_initial_balances_bs_ml_domain(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain

    def _get_initial_balances_pl_ml_domain(self, *args, **kwargs):
        domain = super()._get_initial_balances_pl_ml_domain(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain

    @api.model
    def _get_period_ml_domain(self, *args, **kwargs):
        domain = super()._get_period_ml_domain(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain

    def _get_initial_balance_fy_pl_ml_domain(self, *args, **kwargs):
        domain = super()._get_initial_balance_fy_pl_ml_domain(*args, **kwargs)
        if not self.env.context.get("add_disabled_accounts", ""):
            domain += [("account_id.disable_in_reporting", "=", False)]
        return domain
