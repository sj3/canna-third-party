# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2023 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount_amount = fields.Monetary(
        string="Total Discount Amount",
        readonly=True,
        store=True,
        currency_field="currency_id",
    )
    discount_base_amount = fields.Monetary(
        string="Base Amount before Discount",
        readonly=True,
        store=True,
        currency_field="currency_id",
        help="Sum of the totals of all Order Lines before discount."
        "\nAlso lines without discount are included in this total.",
    )
    commercial_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Commercial Entity",
        compute="_compute_commercial_partner_id",
        store=True,
        readonly=True,
    )
    discount_ids = fields.Many2many(
        comodel_name="sale.discount",
        relation="sale_order_discount_rel",
        column1="order_id",
        column2="discount_id",
        string="Sale Discount engines",
        help="Sale Discount engines for this order.",
    )

    @api.depends("partner_id")
    def _compute_commercial_partner_id(self):
        for so in self:
            so.commercial_partner_id = so.partner_id.commercial_partner_id
            so.discount_ids = [(6, 0, so.commercial_partner_id.sale_discount_ids.ids)]

    @api.onchange("partner_shipping_id", "partner_id", "company_id")
    def onchange_partner_shipping_id(self):
        res = super().onchange_partner_shipping_id()
        self._update_discount()
        return res

    @api.onchange("date_order")
    def _onchange_sale_discount_advanced_date_order(self):
        """
        Expired discounts from the commercial_partner_id may become
        active when changing the date or vice versa.
        Manually added discounts can become expired or vice versa.
        """
        old_discounts = self.discount_ids
        discounts = self.env["sale.discount"]
        for discount in old_discounts + self.commercial_partner_id.sale_discount_ids:
            if discount.active and discount._check_active_date(self.date_order):
                discounts += discount
        if discounts.ids != old_discounts.ids:
            self.discount_ids = [(6, 0, discounts.ids)]

    @api.onchange("discount_ids", "order_line")
    def _onchange_discount_ids(self):
        discounts = self.env["sale.discount"]
        for discount in self.discount_ids:
            if discount.active and discount._check_active_date(self.date_order):
                discounts += discount
        self.discount_ids = [(6, 0, discounts.ids)]
        for line in self.order_line:
            discounts = line._get_sale_discounts()
            # In case we are in an onchange, self is a NewId.
            # By using .ids we get a value that we can use to compare.
            if discounts.ids != line.sale_discount_ids.ids:
                line.sale_discount_ids = [(6, 0, discounts.ids)]
        self._update_discount()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        context = self._context
        if not context.get("sale_discount_advanced"):
            if view_type == "form":
                view_obj = etree.XML(res["arch"])
                order_line = view_obj.xpath("//field[@name='order_line']")
                extra_ctx = (
                    "'sale_discount_advanced': 1, 'so_discount_ids': discount_ids"
                )
                for el in order_line:
                    ctx = el.get("context")
                    if ctx:
                        ctx_strip = ctx.rstrip("}").strip().rstrip(",")
                        ctx = ctx_strip + ", " + extra_ctx + "}"
                    else:
                        ctx = "{" + extra_ctx + "}"
                    el.set("context", str(ctx))
                    res["arch"] = etree.tostring(view_obj)
        return res

    def copy(self, default=None):
        """
        trigger recompute of discounts when duplicating an SO
        """
        dup = super().copy(default=default)
        dup._compute_commercial_partner_id()
        dup._onchange_discount_ids()
        return dup

    def action_draft(self):
        """
        trigger recompute of discounts when a cancelled SO is set back to draft
        """
        res = super().action_draft()
        for rec in self:
            rec._compute_commercial_partner_id()
            rec._onchange_discount_ids()
        return res

    def compute_discount(self):
        """
        cf. module 'sale_order_group_discount'
        """
        for so in self:
            if so.state not in ["draft", "sent"]:
                return
        self._update_discount()

    def _update_discount(self):  # noqa: C901
        if self.env.context.get("skip_discount_calc"):
            return
        grouped_discounts = {}
        base_amount_totals = {}
        line_updates = {}

        orders = self.with_context(dict(self.env.context, skip_discount_calc=True))
        for so in orders:
            is_zero = (
                so.currency_id
                and so.currency_id.is_zero
                or self.env.company.currency_id.is_zero
            )
            total_base_amount = 0.0
            for line in so.order_line:
                base_amount = line.price_unit * line.product_uom_qty
                total_base_amount += base_amount
                for entry in line.sale_discount_ids:
                    if isinstance(entry.id, models.NewId):
                        discount = entry._origin
                    else:
                        discount = entry
                    if discount not in grouped_discounts:
                        grouped_discounts[discount] = line
                    else:
                        grouped_discounts[discount] += line
                if not line.sale_discount_ids:
                    discount = self.env["sale.discount"]
                    if discount not in grouped_discounts:
                        grouped_discounts[discount] = line
                    else:
                        grouped_discounts[discount] += line
            base_amount_totals[so] = total_base_amount

        # redistribute the discount to the lines
        # when discount_base == 'sale_order' | 'sale_order_group'
        for discount, lines in grouped_discounts.items():
            if discount.discount_base == "sale_order":
                for so in orders:
                    so_lines = lines.filtered(lambda r: r.order_id == so)
                    res = discount._calculate_discount(so_lines)
                    self._line_updates(line_updates, so_lines, discount, res)
            elif discount.discount_base == "sale_order_group":
                res = discount._calculate_discount(lines)
                self._line_updates(line_updates, lines, discount, res)
            elif discount.discount_base == "sale_line":
                for line in lines:
                    res = discount._calculate_discount(line)
                    self._line_updates(line_updates, line, discount, res)
            elif not discount:
                res = {x: {"disc_pct": 0.0} for x in lines}
                self._line_updates(line_updates, lines, discount, res)
            else:
                raise NotImplementedError

        line_update_vals = {}
        for line, line_discounts in line_updates.items():
            discount_ids = [x[0].id for x in line_discounts if x[0]]
            line_update_vals[line] = {"sale_discount_ids": [(6, 0, discount_ids)]}
            pct_sum = 0.0
            exclusives = [x for x in line_discounts if x[0].exclusive and x[1]]
            if exclusives:
                exclusives.sort(key=lambda x: x[0].sequence)
                exclusive = exclusives[0]
                pct_exclusive = min(exclusive[1], 100)
                if exclusive[0].exclusive == "highest":
                    pct_other = sum(
                        [x[1] for x in line_discounts if x not in exclusives]
                    )
                    pct_other = min(pct_other, 100.0)
                    if pct_other > pct_exclusive:
                        applied_discount_ids = [
                            x[0].id
                            for x in line_discounts
                            if x not in exclusives and x[1]
                        ]
                        line_update_vals[line] = {
                            "discount": pct_other,
                            "applied_sale_discount_ids": [(6, 0, applied_discount_ids)],
                        }
                    else:
                        applied_discount_ids = exclusive[0].ids
                        line_update_vals[line] = {
                            "discount": pct_exclusive,
                            "applied_sale_discount_ids": [(6, 0, applied_discount_ids)],
                        }
                else:
                    applied_discount_ids = exclusive[0].ids
                    line_update_vals[line] = {
                        "discount": pct_exclusive,
                        "applied_sale_discount_ids": [(6, 0, applied_discount_ids)],
                    }
            else:
                pct_sum = sum([x[1] for x in line_discounts])
                pct_sum = min(pct_sum, 100.0)
                applied_discount_ids = [x[0].id for x in line_discounts if x[0]]
                line_update_vals[line] = {
                    "discount": pct_sum,
                    "applied_sale_discount_ids": [(6, 0, applied_discount_ids)],
                }

        for line in line_update_vals:
            line.update(line_update_vals[line])

        for so in orders:
            vals = {}
            total_discount_amount = 0.0
            for line in so.order_line:
                base_amount = line.price_unit * line.product_uom_qty
                discount_pct = line.discount
                total_discount_amount += base_amount * discount_pct / 100.0
            if not is_zero(so.discount_amount - total_discount_amount):
                vals["discount_amount"] = total_discount_amount
            if not is_zero(so.discount_base_amount - base_amount_totals[so]):
                vals["discount_base_amount"] = base_amount_totals[so]
            if vals:
                so.update(vals)
            if so != so._origin:
                # trigger update of lines on UI
                so.order_line = so.order_line

    def _line_updates(self, line_updates, so_lines, discount, res):
        for line in so_lines:
            if line not in line_updates:
                line_updates[line] = [(discount, res[line]["disc_pct"])]
            else:
                line_updates[line] += [(discount, res[line]["disc_pct"])]
