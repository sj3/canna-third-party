# Copyright 2016-2020 Onestein B.V.
# Copyright 2025 Calin
# Copyright 2025 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv

import xlrd

from odoo import _, fields, models
from odoo.exceptions import UserError


class ImportPriceCatalog(models.TransientModel):
    _name = "import.price.catalog"
    _description = "Import Price Catalogs"

    data = fields.Binary(string="File", required=True)
    subcatalog_id = fields.Many2one(
        comodel_name="price.subcatalog", string="Subcatalog", required=True
    )
    remove_data = fields.Boolean(string="Remove All Data")
    filename = fields.Char(string="File Name", required=True)
    status_report = fields.Text(string="Report")
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )

    # the CSV formatting fields are currently not available on the UI
    csv_delimiter = fields.Selection(
        selection=[(",", ", (comma)"), (";", "; (semicolon)")],
        string="CSV Separator",
        default=";",
    )
    csv_quotechar = fields.Char(
        string="CSV Quote Character",
        default='"',
        help='Character used to quote fields (e.g., "hello, world")',
    )
    csv_decimal_separator = fields.Selection(
        selection=[(".", ". (dot)"), (",", ", (comma)")],
        string="Decimal Separator",
        default=".",
    )
    csv_codepage = fields.Char(
        string="Code Page",
        default="utf-8",
        help="Code Page of the system that has generated the csv file."
        "\nE.g. utf-8, Windows-1252",
    )

    def import_catalog(self):
        if not self.data:
            raise UserError(_("No file uploaded!"))
        file_extension = self.filename.split(".")[-1]
        if file_extension not in ["csv", "xlsx"]:
            raise UserError(_("Only CSV or XLSX files are allowed!"))
        decoded_data = base64.b64decode(self.data)
        if self.remove_data:
            self.subcatalog_id.item_ids.unlink()
        if file_extension == "csv":
            return self._import_csv(decoded_data)
        else:
            return self._import_xlsx(decoded_data)

    def _import_csv(self, data):
        """Process CSV file."""
        decoded_data = data.decode(self.csv_codepage).splitlines()
        reader = csv.reader(
            decoded_data, delimiter=self.csv_delimiter, quotechar=self.csv_quotechar
        )
        catalog_items = []
        for index, row in enumerate(reader):
            if index == 0:
                continue
            product_code = row[0].strip()
            price = row[2].strip()
            if self.csv_decimal_separator == ".":
                price = float(price.replace(",", ""))
            else:
                price = float(price.replace(".", "").replace(",", "."))
            catalog_items.append((product_code, price))
        return self._update_catalog_items(catalog_items)

    def _import_xlsx(self, data):
        """Process XLSX file."""
        workbook = xlrd.open_workbook(file_contents=data)
        sheet = workbook.sheet_by_index(0)
        catalog_items = []
        for row_idx in range(1, sheet.nrows):
            price = sheet.cell(row_idx, 2).value
            if isinstance(sheet.cell(row_idx, 0).value, float):
                product_code = str(int(sheet.cell(row_idx, 0).value))
            else:
                product_code = str(sheet.cell(row_idx, 0).value).strip()
            catalog_items.append((product_code, price))
        return self._update_catalog_items(catalog_items)

    def _update_catalog_items(self, catalog_items):
        if not catalog_items:
            raise UserError(
                _("The Excel file must contain at least one data row after the header.")
            )
        problem_count = 0
        error_messages = []
        for product_code, price in catalog_items:
            product_ids = self.env["product.product"]._search(
                [("default_code", "=", product_code)]
            )
            if not product_ids:
                problem_count += 1
                error_messages.append(f"Product Code: {product_code} not found")
            elif len(product_ids) > 1:
                problem_count += 1
                error_messages.append(
                    f"Product record ambiguity error.\n"
                    "Product Code: {product_code} has been defined multiple times."
                )
            else:
                product_id = product_ids[0]
                vals = {
                    "product_id": product_id,
                    "price": price,
                }
                item = self.subcatalog_id.item_ids.filtered(
                    lambda r: r.product_id.id == product_id
                )
                if item:
                    item.write(vals)
                else:
                    vals["subcatalog_id"] = self.subcatalog_id.id
                    self.env["price.catalog.item"].create(vals)

        self.status_report = (
            "No Problems Occurred" if problem_count == 0 else "\n".join(error_messages)
        )
        result_view = self.env.ref(
            "import_price_catalog.import_price_catalog_view_form_result"
        )
        return {
            "view_type": "form",
            "view_mode": "form",
            "res_model": self._name,
            "res_id": self.id,
            "view_id": result_view.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }
