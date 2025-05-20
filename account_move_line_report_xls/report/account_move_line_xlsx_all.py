# Copyright 2009-2025 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountMoveLineXlsxAll(models.AbstractModel):
    _name = "report.account_move_line_report_xls.account_move_line_xlsx_all"
    _inherit = "report.account_move_line_report_xls.account_move_line_xlsx"
    _description = "Journal Items XLSX export all"

    def generate_xlsx_report(self, workbook, data, objects):
        dom = data["aml_domain"]
        objects = self.env["account.move.line"].search(dom)
        super().generate_xlsx_report(workbook, data, objects)
