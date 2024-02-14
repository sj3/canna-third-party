# Copyright 2009-2024 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpenseLineProductWizard(models.TransientModel):
    _name = "hr.expense.line.product.wizard"
    _description = "Update product on expense line"

    exp_line_id = fields.Many2one(comodel_name="hr.expense", string="HR Expense",)
    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("can_be_expensed", "=", True)],
        string="Product",
        required=True,
    )

    def update(self):
        self.exp_line_id.product_id = self.product_id
        self.exp_line_id.tax_ids = self.product_id.supplier_taxes_id
        account = self.product_id.product_tmpl_id._get_product_accounts()["expense"]
        if account:
            self.exp_line_id.account_id = account
