# Copyright 2009-2022 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpenseLineProductWizard(models.TransientModel):
    _name = "hr.expense.line.product.wizard"
    _description = "Update product on expense line"

    product_id = fields.Many2one(
        comodel_name="product.product",
        domain=[("can_be_expensed", "=", True)],
        string="Product",
        required=True,
    )

    def update(self):
        line = self.env["hr.expense"].browse(self._context.get("active_id"))
        line.product_id = self.product_id
        line.tax_ids = self.product_id.supplier_taxes_id
        account = self.product_id.product_tmpl_id._get_product_accounts()["expense"]
        if account:
            line.account_id = account
