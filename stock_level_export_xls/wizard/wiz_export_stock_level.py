# Copyright 2009-2017 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import io
import json
from datetime import datetime

import xlsxwriter

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, date_utils


class WizExportStockLevel(models.TransientModel):
    _name = "wiz.export.stock.level"
    _description = "Generate a stock level report for a given date"

    stock_level_date = fields.Datetime(
        string="Stock Level Date",
        help="Specify the Date & Time for the Stock Levels."
        "\nThe current stock level will be given if not specified.",
    )
    categ_id = fields.Many2one(
        comodel_name="product.category",
        string="Product Category",
        help="Limit the export to the selected Product Category.",
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse",
        string="Warehouse",
        help="Limit the export to the selected Warehouse.",
    )
    location_id = fields.Many2one(
        comodel_name="stock.location",
        string="Location",
        domain=[("usage", "=", "internal"), ("child_ids", "=", False)],
        help="Limit the export to the selected Location. ",
    )
    product_select = fields.Selection(
        [("all", "All Products"), ("select", "Selected Products")],
        string="Products",
        default=lambda self: self._default_product_select(),
    )
    import_compatible = fields.Boolean(
        string="Import Compatible Export",
        help="Generate a file for use with the 'stock_level_import' module.",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    @api.model
    def _default_product_select(self):
        if self._context.get("active_model") in ["product.product", "product.template"]:
            return "select"
        else:
            return "all"

    @api.constrains("location_id")
    def _check_location_id(self):
        if self.location_id.child_ids:
            raise UserError(_("You cannot select a location which has Child Locations"))

    def _xls_export_domain(self):
        ctx = self._context
        domain = [
            ("type", "in", ["product", "consu"]),
            "|",
            ("active", "!=", "True"),
            ("active", "=", "True"),
            "|",
            ("company_id", "=", self.company_id.id),
            ("company_id", "=", False),
        ]
        if self.categ_id:
            domain.append(("categ_id", "child_of", self.categ_id.id))
        if self.product_select == "select":
            if ctx.get("active_model") == "product.product":
                domain.append(("id", "in", ctx.get("active_ids")))
            elif ctx.get("active_model") == "product.template":
                products = self.env["product.product"].search(
                    [("product_tmpl_id", "in", ctx.get("active_ids"))]
                )
                domain.append(("id", "in", products._ids))
        return domain

    def _update_datas(self, datas):
        """
        Update datas when adding extra options to the wizard
        in inherited modules.
        """
        pass

    def xls_export(self):
        self.ensure_one()
        warehouses = self.warehouse_id
        if not warehouses:
            warehouses = self.env["stock.warehouse"].search(
                [("company_id", "=", self.company_id.id)]
            )
        warehouse_ids = warehouses._ids
        domain = self._xls_export_domain()
        products = self.env["product.product"].search(domain)

        if not products:
            raise UserError(
                _(
                    """No Data Available,
                No records found for your selection !"""
                )
            )

        if self.location_id:
            warehouse_id = self.location_id.get_warehouse()
            if not warehouse_id:
                raise UserError(
                    _("No Warehouse defined for the selected " "Stock Location ")
                )
            warehouse_ids = warehouse_id.id

        datas = {
            "model": self._name,
            "stock_level_date": self.import_compatible
            and False
            or self.stock_level_date,
            "product_ids": products._ids,
            "category_id": self.categ_id.name,
            "warehouse_ids": warehouse_ids,
            "location_id": self.location_id.id,
            "product_select": self.product_select,
            "import_compatible": self.import_compatible,
            "company_id": self.company_id.id,
        }
        self._update_datas(datas)

        return {
            "type": "ir_actions_xlsx_download",
            "data": {
                "model": "wiz.export.stock.level",
                "options": json.dumps(datas, default=date_utils.json_default),
                "output_format": "xlsx",
                "report_name": "Excel Report",
            },
        }

    def get_xlsx_report(self, data, response):
        product_obj = self.env["product.product"]
        context = dict(self._context)
        wanted_list = product_obj._stock_level_export_xls_fields()
        context.update({"wanted_list": wanted_list})
        warehouse = data.get("warehouse_ids")
        warehouse = self.env["stock.warehouse"].search([("id", "=", warehouse)])

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        if len([warehouse]) == 1:
            worksheet = workbook.add_worksheet(warehouse.name)
        else:
            worksheet = workbook.add_worksheet("Reporting")

        header_format = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "border": True,
                "bold": True,
                "fg_color": "#dbeef4",
            }
        )
        record_format = workbook.add_format(
            {"font_name": "Arial", "font_size": 11, "border": True}
        )

        row = 0
        col = 0
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 30)
        worksheet.set_column("C:C", 30)
        worksheet.set_column("D:D", 15)
        worksheet.set_column("E:E", 15)
        worksheet.set_column("F:F", 15)
        worksheet.set_column("G:G", 15)
        worksheet.set_column("H:H", 55)
        worksheet.set_column("I:I", 10)
        worksheet.set_column("J:J", 10)
        worksheet.set_column("K:K", 15)

        row += 2
        worksheet.set_row(row, cell_format=record_format)
        worksheet.write(row, col, "Product Category")
        worksheet.write(row, col + 1, data.get("category_id"))

        row += 2

        worksheet.set_row(row, cell_format=header_format)
        worksheet.write(row, col, "Product Reference")
        worksheet.write(row, col + 1, "Product Name")
        worksheet.write(row, col + 2, "Product Category")
        worksheet.write(row, col + 3, "Product UOM")
        worksheet.write(row, col + 4, "Quantity")
        worksheet.write(row, col + 5, "Cost")
        worksheet.write(row, col + 6, "Stock Value")
        worksheet.write(row, col + 7, "Stock Location")
        worksheet.write(row, col + 8, "Location ID")
        worksheet.write(row, col + 9, "Product ID")
        worksheet.write(row, col + 10, "Product UOM ID")
        if len([warehouse]) > 1:
            # create "all warehouses" overview report
            self._warehouse_report(
                data, worksheet, workbook, context, self.env["stock.warehouse"]
            )
        for warehouse in warehouse:
            self._warehouse_report(data, worksheet, workbook, context, warehouse)

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()

    def _get_stock_data(self, data, warehouse):
        ctx = dict(self._context)
        ctx["force_company"] = data["company_id"]
        if warehouse:
            ctx["warehouse"] = warehouse.id
        if data["stock_level_date"]:
            ctx["to_date"] = data["stock_level_date"]
        else:
            ctx["to_date"] = fields.Datetime.now()
        product_lines = []
        if data["location_id"]:
            location = self.env["stock.location"].browse(data["location_id"])
            products = (
                self.env["product.product"]
                .with_context(dict(ctx, location=data["location_id"]))
                .browse(data["product_ids"])
            )
            for product in products:
                #                product.location_id = location.id
                product.location = location.name
                product_lines.append(product)
        else:
            products = (
                self.env["product.product"]
                .with_context(ctx)
                .browse(data["product_ids"])
            )
            for product in products:
                product.location = False
                product_lines.append(product)
        extras = products._compute_cost_and_qty_available_at_date()
        report_lines = []
        for product in product_lines:
            qty, cost = extras[product.id]
            if not qty and not data["import_compatible"]:
                # Drop empty lines if output is a stock valuation report.
                # Keep those lines if output is intended for
                # import with new inventory values.
                continue
            product.qty_available_at_date = qty
            product.cost_at_date = cost
            report_lines.append(product)
        return report_lines

    def _warehouse_report(self, data, worksheet, workbook, context, warehouse):
        product_lines = self._get_stock_data(data, warehouse)
        warehouse = data.get("warehouse_ids")
        if warehouse and not product_lines and len([warehouse]) > 1:
            return

        wanted_list = context.get("wanted_list")
        if data.get("import_compatible"):
            for x in ["location", "location_id", "product_id", "product_uom_id"]:
                if x not in wanted_list:
                    wanted_list.append(x)

        cost_pos = "cost" in wanted_list and wanted_list.index("cost")
        quantity_pos = "quantity" in wanted_list and wanted_list.index("quantity")
        if not (cost_pos and quantity_pos) and "stock_value" in wanted_list:
            raise UserError(
                _("Customization Error !"),
                _(
                    "The 'Stock Value' field is a calculated XLS field "
                    "requiring the presence of "
                    "the 'Cost' and 'Quantity' fields!"
                ),
            )

        warehouse = self.env["stock.warehouse"].search([("id", "=", warehouse)])

        if warehouse:
            sheet_name = warehouse.name
            report_name = _("Warehouse") + " " + sheet_name + " - "
        else:
            sheet_name = _("All Warehouses")
            report_name = sheet_name + " - "

        stock_level_date = data["stock_level_date"] or fields.Datetime.now()
        stock_level_date_dt = stock_level_date

        if isinstance(stock_level_date_dt, str):
            stock_level_date_dt = datetime.strptime(
                stock_level_date_dt, DEFAULT_SERVER_DATETIME_FORMAT
            )

        stock_level_date_dt_fmt = datetime.strftime(
            stock_level_date_dt, DEFAULT_SERVER_DATETIME_FORMAT
        )
        report_name += _("Stock Levels at %s") % stock_level_date_dt_fmt

        row = 0
        col = 0
        header_format = workbook.add_format(
            {"font_name": "Arial", "font_size": 14, "bold": True}
        )
        record_format = workbook.add_format({"font_name": "Arial", "font_size": 11})
        total_format = workbook.add_format(
            {
                "font_name": "Arial",
                "font_size": 12,
                "border": True,
                "bold": True,
                "fg_color": "#dbeef4",
            }
        )

        worksheet.write(row, col, report_name, header_format)
        row = 5

        # Product lines
        stock_val_list = []
        for product in product_lines:
            stock_value = product.qty_available_at_date * product.cost_at_date

            worksheet.write(row, col, product.default_code, record_format)
            worksheet.write(row, col + 1, product.name, record_format)
            worksheet.write(row, col + 2, product.categ_id.name, record_format)
            worksheet.write(row, col + 3, product.uom_id.name, record_format)
            worksheet.write(row, col + 4, product.qty_available_at_date, record_format)
            worksheet.write(row, col + 5, product.cost_at_date, record_format)
            worksheet.write(row, col + 6, stock_value, record_format)
            worksheet.write(row, col + 7, product.location, record_format)
            worksheet.write(row, col + 8, data.get("location_id"), record_format)
            worksheet.write(row, col + 9, product.id, record_format)
            worksheet.write(row, col + 10, product.uom_id.id, record_format)

            stock_val_list.append(stock_value)
            row += 1

        stock_total = sum(stock_val_list)
        worksheet.set_row(row, cell_format=total_format)
        worksheet.write(row, col + 6, stock_total)
