# Copyright 2009-2024 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    @api.depends(
        "sheet_id",
        "sheet_id.account_move_id",
        "sheet_id.state",
        "sheet_id.update_sheet_lines",
    )
    def _compute_state(self):
        for expense in self:
            if expense.sheet_id.update_sheet_lines:
                expense.state = "draft"
            else:
                super()._compute_state()

    def update_product(self):
        module = __name__.split("addons.")[1].split(".")[0]
        view = self.env.ref("%s.hr_expense_line_product_wizard_view_form" % module)
        ctx = dict(
            self.env.context,
            default_exp_line_id=self.id,
            default_product_id=self.product_id.id,
        )
        return {
            "name": _("Update Product"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "hr.expense.line.product.wizard",
            "view_id": view.id,
            "target": "new",
            "type": "ir.actions.act_window",
            "context": ctx,
        }
