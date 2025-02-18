# Copyright 2016-2020 Onestein B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import xlrd
from odoo import _,api,models, fields
from odoo.exceptions import UserError


class ImportPriceCatalog(models.TransientModel):
    _name = "import.price.catalog"
    _description = "Import Price Catalogs"

    data = fields.Binary("File", required=True)
    subcatalog_id = fields.Many2one(
        comodel_name="price.subcatalog", string="Subcatalog", required=True
    )
    company_id = fields.Many2one("res.company", "Company")
    remove_data = fields.Boolean("Remove All Data")
    filename = fields.Char("File Name", required=True)

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list=fields_list)
        if "company_id" in fields_list:
            company = self.env["res.company"].search([])
            defaults.update({"company_id": company[0].id})
        return defaults

    def import_catalog(self):
        if not self.data:
            raise UserError("No file uploaded!")
        file_extension = self.filename.split('.')[-1]
        if file_extension not in ['csv', 'xlsx']:
            raise UserError("Only CSV or XLSX files are allowed!")
        decoded_data = base64.b64decode(self.data)
        price_catalog_item = self.env["price.catalog.item"]
        if self.remove_data:
            catalog_data_delete = price_catalog_item.search(
                [("subcatalog_id", "=", self.subcatalog_id.id)]
            )
            for item in catalog_data_delete:
                item.unlink()
        if file_extension == 'csv':
            return self._import_csv(decoded_data,self.subcatalog_id)
        else:
            return self._import_xlsx(decoded_data,self.subcatalog_id)


    def _import_csv(self, data,catalog_id):
        """Process CSV file."""
        decoded_data = data.decode('utf-8').splitlines()
        reader = csv.reader(decoded_data)
        problem_count = 0
        error_messages= []
        product = self.env["product.product"]
        price_catalog_item = self.env["price.catalog.item"]
        for index, row in enumerate(reader):
            if index == 0:
                continue
            product_code, price = row[0].strip(), row[2].strip()
            product_id = product.search([('default_code', '=', str(product_code))], limit=1)
            if product_id:
                product_id = product_id[0]
                vals = {
                    "subcatalog_id": catalog_id.id,
                    "product_id": product_id.id,
                    "price": price,
                }
                price_catalog_item.create(vals)
            else:
                problem_count += 1
                error_messages.append(f"Product Code: {product_code} not found")
        error_mess = "\n".join(error_messages)
        status_report = "No Problems Occurred" if problem_count == 0 else error_mess
        return self._get_action(status_report)


    def _import_xlsx(self, data,catalog_id):
        """Process XLSX file."""
        workbook = xlrd.open_workbook(file_contents=data)
        sheet = workbook.sheet_by_index(0)
        if sheet.nrows <= 1:
            raise  UserError(_("The Excel file must contain at least one data row after the header."))
        problem_count = 0
        error_messages = []
        product = self.env["product.product"]
        price_catalog_item = self.env["price.catalog.item"]
        for row_idx in range(1, sheet.nrows):
            price = sheet.cell(row_idx, 2).value
            if isinstance(sheet.cell(row_idx, 0).value, float):
                product_code = str(int(sheet.cell(row_idx, 0).value))
            else:
                product_code = str(sheet.cell(row_idx, 0).value)
            product_id = product.search([('default_code', '=', product_code)], limit=1)
            if product_id:
                product_id = product_id[0]
                vals = {
                    "subcatalog_id": catalog_id.id,
                    "product_id": product_id.id,
                    "price": price,
                }
                price_catalog_item.create(vals)
            else:
                problem_count += 1
                error_messages.append(f"Product Code: {product_code} not found")
        error_mess = "\n".join(error_messages)
        status_report = "No Problems Occurred" if problem_count == 0 else error_mess
        return self._get_action(status_report)

    def _get_action(self, status_report):
        """Return action to open the form view with a status report."""
        obj_model = self.env["ir.model.data"]
        model_data_ids = obj_model.search(
            [("model", "=", "ir.ui.view"), ("name", "=", "data_price_catalog_view_form")]
        )
        if not model_data_ids:
            raise UserError(_("Could not find the data.price.catalog.form view"))
        resource_id = model_data_ids.read(fields=["res_id"])[0]["res_id"]
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": "data.price.catalog",
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
            "context": self.with_context(status_report=status_report)._context,
        }

class DataPriceCatalog(models.TransientModel):
    _name = "data.price.catalog"
    _description = "Data Price Catalog"
    status_report = fields.Text("Report")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list=fields_list)
        if self._context.get("status_report", False):
            defaults.update({"status_report": self._context["status_report"]})
        return defaults




