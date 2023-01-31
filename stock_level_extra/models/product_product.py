# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openerp import api, models
from openerp.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def _get_domain_dates(self):
        from_date = self.env.context.get("from_date", False)
        to_date = self.env.context.get("to_date", False)
        domain = []
        if from_date:
            domain.append(("date", ">=", from_date))
        if to_date:
            domain.append(("date", "<=", to_date))
        return domain

    def get_stock_level(self):
        """Compute stock level at date using stock moves.
        """
        context = self._context
        res = {}

        domain_move_in, domain_move_out = [], []
        (
            domain_quant_loc,
            domain_move_in_loc,
            domain_move_out_loc,
        ) = self._get_domain_locations()
        domain_dates = self._get_domain_dates()
        domain_move_in += domain_dates
        domain_move_in += [("state", "=", "done")]
        domain_move_out += domain_dates
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
            res[product.id] = in_qty - out_qty

        return res

