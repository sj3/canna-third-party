# Copyright 2009-2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleDiscount(models.Model):
    _inherit = "sale.discount"

    def _calculate_discount(self, lines):
        res = super()._calculate_discount(lines)
        pallet_rules = self.rule_ids.filtered(lambda r: r.matching_type == "pallet")
        for rule in pallet_rules.filtered(lambda r: r._pallet_matching(lines)):
            for sol in res:
                base = res[sol]["base"]
                qty = res[sol]["qty"]
                if rule.discount_type == "perc":
                    disc_amt = base * rule.discount_pct / 100.0
                    disc_pct = rule.discount_pct
                else:
                    if rule.matching_type == "quantity" and len(rule.product_ids) == 1:
                        disc_amt = min(rule.discount_amount_unit * qty, base)
                    else:
                        disc_amt = min(rule.discount_amount, base)
                    disc_pct = disc_amt / base * 100.0
                res[sol].update(
                    {
                        "disc_amt": res[sol]["disc_amt"] + disc_amt,
                        "disc_pct": res[sol]["disc_pct"] + disc_pct,
                    }
                )
        return res
