# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2023 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import MAXYEAR, MINYEAR, date

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class SaleDiscount(models.Model):
    _name = "sale.discount"
    _description = "Sale Order Discount"
    _inherit = "mail.thread"
    _order = "sequence"

    sequence = fields.Integer()
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    name = fields.Char(string="Discount", tracking=True, required=True)
    start_date = fields.Date(string="Start date", tracking=True)
    end_date = fields.Date(string="End date", tracking=True)
    active = fields.Boolean(
        string="Discount active",
        tracking=True,
        default=lambda self: self._default_active(),
    )
    discount_base = fields.Selection(
        selection=lambda self: self._selection_discount_base(),
        string="Discount Base",
        required=True,
        default="sale_order_group",
        tracking=True,
        help="Base the discount on ",
    )
    exclusive = fields.Selection(
        selection=[("always", "Always"), ("highest", "Use Highest")],
        string="Exclusive",
        help="This discount engine will be used exclusively for the "
        "sale order line discount calculation "
        "if a rule of this engine matches for the line."
        "\nThe order of the discount object will determine which one of "
        "the 'exclusive' discount engines will be selected "
        "in case multiple 'exclusive' discount objects have been set "
        "on this sales order (the order is set via the discount "
        "'sequence' field, the lowest sequence will be selected)."
        "\nThe 'Use Highest' option will change this behaviour: "
        "when the granted exclusive discount is lower than the sum of "
        "the discounts calculated by the other discount engines "
        "than the exclusive discount will be dropped "
        "in favour of the other engines.",
    )
    rule_ids = fields.One2many(
        comodel_name="sale.discount.rule",
        inverse_name="sale_discount_id",
        string="Discount Rules",
        tracking=True,
    )
    excluded_product_category_ids = fields.Many2many(
        comodel_name="product.category",
        string="Excluded Product Categories",
        tracking=True,
        help="Products in these categories will by default be excluded "
        "from this discount.",
    )
    excluded_product_ids = fields.Many2many(
        comodel_name="product.product",
        string="Excluded Products",
        tracking=True,
        help="These products will by default be excluded " "from this discount.",
    )
    included_product_category_ids = fields.Many2many(
        comodel_name="product.category",
        relation="product_category_sale_discount_incl_rel",
        string="Included Product Categories",
        tracking=True,
        help="Fill in this field to limit the discount calculation "
        "to Products in these categories.",
    )
    included_product_ids = fields.Many2many(
        comodel_name="product.product",
        relation="product_sale_discount_incl_rel",
        string="Included Products",
        tracking=True,
        help="Fill in this field to limit the discount calculation "
        "to these products.",
    )

    @api.model
    def _default_active(self):
        return True

    @api.model
    def _selection_discount_base(self):
        """
        Separate method to allow the removal of an option
        via inherit.
        """
        selection = [
            ("sale_order", "Base discount on order"),
            ("sale_order_group", "Base discount on group of orders"),
            ("sale_line", "Base discount on order line"),
        ]
        return selection

    @api.onchange("discount_base")
    def _onchange_discount_base(self):
        self.exclusive = False
        self.rule_ids.update(
            {
                "matching_type": "amount",
                "product_ids": False,
                "product_category_ids": False,
                "discount_type": "perc",
                "discount_pct": 0.0,
                "discount_amount": 0.0,
                "discount_amount_unit": 0.0,
            }
        )

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        if self.start_date and self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError(
                    _("The end date may not be lower than the start date.")
                )

    def _creation_subtype(self):
        return self.env.ref("sale_discount_advanced.mt_discount_new")

    def _track_subtype(self, init_values):
        self.ensure_one()
        if "active" in init_values:
            return self.env.ref("sale_discount_advanced.mt_discount_active")
        if "start_date" in init_values:
            return self.env.ref("sale_discount_advanced.mt_discount_start_date")
        if "end_date" in init_values:
            return self.env.ref("sale_discount_advanced.mt_discount_end_date")
        return super()._track_subtype(init_values)

    def unlink(self):
        if self.env["sale.order.line"].search_count(
            [("sale_discount_ids", "in", self.ids)]
        ):
            raise UserError(
                _("You cannot delete a discount which is used in a Sale Order!")
            )
        return super().unlink()

    def _check_active_date(self, check_date=None):
        if not check_date:
            check_date = fields.Date.today()
        else:
            check_date = fields.Datetime.context_timestamp(
                self.env.user, check_date
            ).date()
        start_date = self.start_date or date(MINYEAR, 1, 1)
        end_date = self.end_date or date(MAXYEAR, 12, 31)
        return start_date <= check_date <= end_date

    def _calculate_discount(self, lines):  # noqa: C901
        result = {}
        qty = sum([x.product_uom_qty for x in lines])
        base = sum([x.product_uom_qty * x.price_unit for x in lines])

        for sol in lines:
            disc_amt = disc_pct = 0.0
            for rule in self.rule_ids:
                if not rule._sol_product_match(sol):
                    continue

                rule_match = False
                if rule.matching_type == "amount":
                    match_min = match_max = False
                    base = self._round_amt_qty(base, "min_base")
                    rule_min_base = self._round_amt_qty(rule.min_base, "min_base")
                    rule_max_base = self._round_amt_qty(rule.max_base, "min_base")
                    if rule_min_base > 0 and rule_min_base > base:
                        continue
                    else:
                        match_min = True
                    if rule_max_base > 0 and rule_max_base < base:
                        continue
                    else:
                        match_max = True
                    rule_match = match_min and match_max
                elif rule.matching_type == "quantity":
                    match_min = match_max = False
                    qty = sol.product_uom_qty
                    qty = self._round_amt_qty(qty, "min_qty")
                    rule_min_qty = self._round_amt_qty(rule.min_qty, "min_qty")
                    rule_max_qty = self._round_amt_qty(rule.max_qty, "min_qty")
                    if rule_min_qty > 0 and rule_min_qty > qty:
                        continue
                    else:
                        match_min = True
                    if rule_max_qty > 0 and rule_max_qty < qty:
                        continue
                    else:
                        match_max = True
                    rule_match = match_min and match_max
                else:
                    method = rule._matching_type_methods().get(rule.matching_type)
                    if not method:
                        raise UserError(
                            _(
                                "Programming error: no method defined for "
                                "matching_type '%s'."
                            )
                            % rule.matching_type
                        )
                    rule_match = getattr(rule, method)(sol)

                if rule_match:
                    if rule.matching_extra != "none":
                        method = rule._matching_extra_methods().get(rule.matching_extra)
                        if not method:
                            raise UserError(
                                _(
                                    "Programming error: no method defined for "
                                    "matching_extra '%s'."
                                )
                                % rule.matching_extra
                            )
                        if not getattr(rule, method)(sol):
                            # The extra matching condition is only applied if all
                            # other conditions match. If the extra matching
                            # condition returns False, then do not apply this rule.
                            rule_match = False
                            continue
                    if rule.discount_type == "perc":
                        disc_amt = base * rule.discount_pct / 100.0
                        disc_pct = rule.discount_pct
                    else:
                        if (
                            rule.matching_type == "quantity"
                            and len(rule.product_ids) == 1
                        ):
                            disc_amt = min(rule.discount_amount_unit * qty, base)
                        else:
                            disc_amt = min(rule.discount_amount, base)
                        disc_pct = disc_amt / base * 100.0
                    # Do not apply any other rules for this discount.
                    break

            # Remark:
            # Only the 'disc_amt' value is used in the code calling this method.
            # We could hence simply the code via result[sol] = disc_amt.
            # Returning more values facilitates the tracing when working on bugs
            # or enhancements for this module.
            result[sol] = {
                "qty": qty,
                "base": base,
                "disc_amt": disc_amt,
                "disc_pct": disc_pct,
            }

        return result

    def _round_amt_qty(self, val, field_name):
        digits = (
            self.env["sale.discount.rule"]._fields[field_name].get_digits(self.env)[1]
        )
        return round(val, digits)

    def _check_product_filter(self, product):
        """
        Checks if the discount object applies to the given product
        """
        self.ensure_one()
        if self._is_excluded_product(product):
            return False
        else:
            product_filter = (
                self.included_product_ids or self.included_product_category_ids
            )
            if product_filter:
                return self._is_included_product(product) and True or False
        return True

    def _is_excluded_product(self, product):
        self.ensure_one()
        # In case we are in an onchange, self is a NewId.
        # By using .ids we get a value that we can use to compare.
        c1 = product.id in self.excluded_product_ids.ids
        c2 = False
        for categ in self.excluded_product_category_ids:
            if product._belongs_to_category(categ):
                c2 = True
                break
        return c1 or c2

    def _is_included_product(self, product):
        self.ensure_one()
        # In case we are in an onchange, self is a NewId.
        # By using .ids we get a value that we can use to compare.
        c1 = product.id in self.included_product_ids.ids
        c2 = False
        for categ in self.included_product_category_ids:
            if product._belongs_to_category(categ):
                c2 = True
                break
        return c1 or c2
