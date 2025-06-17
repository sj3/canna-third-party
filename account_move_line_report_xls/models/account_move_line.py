# Copyright 2009-2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)

_render = ReportXlsxAbstract._render


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def aml_export_all(self, domain):
        xmlid = "account_move_line_report_xls.action_account_move_line_xlsx_all"
        docids = None
        data = {"aml_domain": domain}
        act = self.env.ref(xmlid).report_action(docids, data=data)
        return act

    # Change list in custom module e.g. to add/drop columns or change order
    @api.model
    def _report_xlsx_fields(self):
        return [
            "move",
            "name",
            "date",
            "journal",
            "partner",
            "account",
            "date_maturity",
            "debit",
            "credit",
            "balance",
            "full_reconcile",
            "reconcile_amount",
            # 'analytic_account_name', 'analytic_account',
            # 'ref', 'partner_ref',
            # 'amount_residual', 'amount_currency', 'currency_name',
            # 'company_currency', 'amount_residual_currency',
            # 'product', 'product_ref', 'product_uom', 'quantity',
            # 'statement', 'invoice', 'narration', 'blocked',
            # 'id', 'matched_debit_ids', 'matched_credit_ids',
        ]

    # Change/Add Template entries
    @api.model
    def _report_xlsx_template(self):
        """
        Template updates, e.g.

        my_change = {
            'move': {
                'header': {
                    'value': 'My Move Title',
                },
                'lines': {
                    'value': _render("line.move_id.name or ''"),
                },
                'width': 20,
            },
        }
        return my_change
        """
        return {}
