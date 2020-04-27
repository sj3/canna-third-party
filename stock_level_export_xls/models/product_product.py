# Copyright 2009-2017 Noviat.
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_cost_at_date(self, product, dt):
        """
        return cost at date for cost_method != 'real'
        """
        valuation_layer = self.env["stock.valuation.layer"].search(
            [("create_date", "=", dt)]
        )

        return valuation_layer.product_id.standard_price

    def _compute_cost_and_qty_available_at_date(self):
        # logic based on _product_available method from standard addons
        context = self._context
        res = {}
        if not context.get("to_date"):
            for product in self:
                res[product.id] = (product.qty_available, product.standard_price)
            return res

        domain_move_in, domain_move_out = [], []
        (
            domain_quant_loc,
            domain_move_in_loc,
            domain_move_out_loc,
        ) = self._get_domain_locations()
        #        domain_dates = self._get_domain_dates()
        #        domain_dates = self._compute_quantities_dict()
        #        domain_move_in += domain_dates
        domain_move_in += [("state", "=", "done")]
        #        domain_move_out += domain_dates
        domain_move_out += [("state", "=", "done")]

        if context.get("owner_id"):
            owner_domain = ("restrict_partner_id", "=", context["owner_id"])
            domain_move_in.append(owner_domain)
            domain_move_out.append(owner_domain)

        domain_move_in += domain_move_in_loc
        domain_move_out += domain_move_out_loc

        domain_products = [("product_id", "in", self._ids)]
        moves_in = self.env["stock.move"].read_group(
            domain_move_in + domain_products,
            ["product_id", "product_qty"],
            ["product_id"],
        )
        moves_out = self.env["stock.move"].read_group(
            domain_move_out + domain_products,
            ["product_id", "product_qty"],
            ["product_id"],
        )

        moves_in = dict(map(lambda x: (x["product_id"][0], x["product_qty"]), moves_in))
        moves_out = dict(
            map(lambda x: (x["product_id"][0], x["product_qty"]), moves_out)
        )

        for product in self:
            in_qty = float_round(
                moves_in.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding,
            )
            out_qty = float_round(
                moves_out.get(product.id, 0.0),
                precision_rounding=product.uom_id.rounding,
            )
            qty_available_at_date = in_qty - out_qty

            cost = 0.0
            # skip calculation when 0.0 qty
            if qty_available_at_date:
                if product.cost_method != "real":
                    cost = self._get_cost_at_date(product, context["to_date"])
                if not cost:
                    # retrieve cost from stock_history view
                    # this should only be needed for cost_method = real
                    # but we also fall back to this view for cases
                    # where the product_price_history table is not correct,
                    # e.g. incorrectly migrated databases
                    domain_product = [("product_id", "=", product.id)]
                    if moves_in:
                        in_ids = (
                            self.env["stock.move"]
                            .search(domain_move_in + domain_product)
                            .ids
                        )
                    else:
                        in_ids = []
                    if moves_out:
                        out_ids = (
                            self.env["stock.move"]
                            .search(domain_move_out + domain_product)
                            .ids
                        )
                    else:
                        out_ids = []
                    move_ids = in_ids + out_ids

                    if move_ids:
                        query = """
                            SELECT quantity, value
                            FROM stock_valuation_layer
                            WHERE id in %s
                            """
                        if context.get("location"):
                            query += " AND location_id = %s" % context["location"]
                        self._cr.execute(query, [tuple(move_ids)])
                        histories = self._cr.dictfetchall()
                        sum = 0.0
                        for h in histories:
                            sum += h["quantity"] * h["value"]
                        cost = sum / qty_available_at_date
            res[product.id] = (qty_available_at_date, cost)
        return res

    @api.model
    def _stock_level_export_xls_fields(self):
        """
        adapt list in custom module to add/drop columns or change order
        """
        return [
            # Inventory fields
            "ref",
            "name",
            "category",
            "uom",
            "quantity",
            # Stock Valuation fields
            "cost",
            "stock_value",
        ]

    @api.model
    def stock_level_export_xls_template(self):
        """
        Template updates, e.g.

        res = super(ProductProduct, self).stock_level_export_xls_template()
        res.update({
            'name': {
                'header': [1, 42, 'text', _render("_('Name')")],
                'products': [1, 0, 'text', _render("product.name or ''")],
                'totals': [1, 0, 'text', None]},
        })
        return res
        """
        return {}
