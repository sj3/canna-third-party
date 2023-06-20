# Copyright 2009-2023 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import api, models

# Copy commented lines infra to your custom module if you want
# to modify the excel template for your own specific needs.
# from odoo.addons.report_xlsx_helper.report.abstract_report_xlsx \
#    import AbstractReportXlsx
# _render = AbstractReportXlsx._render

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_domain_locations_new(
        self, location_ids, company_id=False, compute_child=True
    ):
        """
        bypass of bug in standard Odoo, cf.
        https://github.com/odoo/odoo/blob/ce1d5c86bd2fc7065f47d11b849da5445ddf02b7
        /addons/stock/models/product.py#L297 :
        domain = company_id and ['&', ('company_id', '=', company_id)] or []

        incorrect domain returned when using force_company.
        """
        domains = super()._get_domain_locations_new(
            location_ids, company_id=company_id, compute_child=compute_child
        )
        new_domains = []
        for dom in domains:
            if dom and dom[0] == "&" and len(dom) == 2:
                dom.pop(0)
            new_domains.append(dom)
        return tuple(new_domains)

    def _add_cost_at_date(self, res):
        for product in self:
            res[product.id]["cost"] = (
                product.quantity_svl and product.value_svl / product.quantity_svl or 0.0
            )

    def _compute_cost_and_qty_available_at_date(self):
        lot_id = self.env.context.get("lot_id")
        owner_id = self.env.context.get("owner_id")
        package_id = self.env.context.get("package_id")
        # from_date not available via UI
        from_date = self.env.context.get("from_date")
        to_date = self.env.context.get("to_date")
        res = self._compute_quantities_dict(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
        )
        if self.env.context.get("add_cost_at_date"):
            self._add_cost_at_date(res)
        return res

    @api.model
    def _stock_level_export_xls_fields(self):
        """
        adapt list in custom module to add/drop columns or change order
        """
        return [
            "ref",
            "name",
            "category",
            "uom",
            "quantity",
            "cost_at_date",
            "qty_x_cost",
            "active",
        ]

    @api.model
    def _stock_level_export_xls_template(self):
        """
        Template updates, e.g.

        res = super(ProductProduct, self)._stock_level_export_xls_template()
        res.update({
            'name': {
                'header': {
                    'type': 'string',
                    'value': _('Product Name'),
                },
                'lines': {
                    'type': 'string',
                    'value': _render(
                        "line.name + (line['product'].default_code or '')"),
                },
                'width': 42,
            },
        })
        return res
        """
        return {}
