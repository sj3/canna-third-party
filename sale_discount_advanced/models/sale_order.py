# -*- coding: utf-8 -*-
# Copyright (C) 2015 ICTSTUDIO (<http://www.ictstudio.eu>).
# Copyright (C) 2016-2019 Noviat nv/sa (www.noviat.com).
# Copyright (C) 2016 Onestein (http://www.onestein.eu/).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from lxml import etree

from openerp import api, fields, models
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    discount_amount = fields.Float(
        digits=dp.get_precision('Account'),
        string='Total Discount Amount',
        readonly=True,
        store=True)
    discount_base_amount = fields.Float(
        digits=dp.get_precision('Account'),
        string='Base Amount before Discount',
        readonly=True,
        store=True,
        help="Sum of the totals of all Order Lines before discount."
             "\nAlso lines without discount are included in this total.")
    discount_ids = fields.Many2many(
        string='Sale Discount engines',
        comodel_name='sale.discount',
        relation='sale_order_discount_rel',
        column1='order_id',
        column2='discount_id',
        help="Sale Discount engines for this order.")

    @api.onchange('discount_ids')
    def _onchange_discount_ids(self):
        self.ensure_one()
        for line in self.order_line:
            discounts = line._get_sale_discounts()
            if discounts != line.sale_discount_ids:
                line.sale_discount_ids = discounts
                line.discount = 0.0

    @api.multi
    def onchange_partner_id_with_date(self, partner_id, date_order):
        res = super(
            SaleOrder, self).onchange_partner_id(partner_id)
        if partner_id and not self or len(self) == 1:
            partner = self.env['res.partner'].browse(partner_id)
            cpartner = partner.commercial_partner_id
            discounts = cpartner._get_active_sale_discounts(date_order)
            res['value']['discount_ids'] = [(6, 0, discounts.ids)]
        return res

    @api.onchange('date_order')
    def _onchange_date_order(self):
        self.ensure_one()
        if self.partner_id:
            cpartner = self.partner_id.commercial_partner_id
            old_discounts = self.discount_ids
            new_discounts = cpartner._get_active_sale_discounts(
                self.date_order)
            if old_discounts != new_discounts:
                self.discount_ids -= old_discounts
                self.discount_ids += new_discounts

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        order.compute_discount()
        return order

    @api.multi
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        for order in self:
            if not self._context.get('discount_calc'):
                order.compute_discount()
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type=False,
                        toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        context = self._context
        if not context.get('sale_discount_advanced'):
            if view_type == 'form':
                view_obj = etree.XML(res['arch'])
                order_line = view_obj.xpath("//field[@name='order_line']")
                extra_ctx = "'sale_discount_advanced': 1, " \
                    "'discount_ids': discount_ids"
                for el in order_line:
                    ctx = el.get('context')
                    if ctx:
                        ctx_strip = ctx.rstrip("}").strip().rstrip(",")
                        ctx = ctx_strip + ", " + extra_ctx + "}"
                    else:
                        ctx = "{" + extra_ctx + "}"
                    el.set('context', str(ctx))
                    res['arch'] = etree.tostring(view_obj)
        return res

    @api.multi
    def button_dummy(self):
        res = super(SaleOrder, self).button_dummy()
        self.compute_discount()
        return res

    @api.multi
    def action_button_confirm(self):
        self.compute_discount()
        return super(SaleOrder, self).action_button_confirm()

    @api.multi
    def compute_discount(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                return
            order._update_discount()

    def _update_discount(self):
        self.ensure_one()
        if self._context.get('discount_calc'):
            return

        grouped_discounts = {}
        total_base_amount = 0.0
        line_updates = {}

        for line in self.order_line:
            base_amount = line.price_unit * line.product_uom_qty
            total_base_amount += base_amount
            line_discounts = []
            for discount in line.sale_discount_ids:
                if discount.discount_base == 'sale_order':
                    if discount.id not in grouped_discounts:
                        grouped_discounts[discount.id] = {
                            'sale_discount': discount,
                            'lines': line}
                    else:
                        grouped_discounts[discount.id]['lines'] += line
                elif discount.discount_base == 'sale_line':
                    match, pct = discount._calculate_line_discount(line)
                    if match:
                        line_discounts += [(discount, pct)]
                else:
                    raise NotImplementedError
            line_updates[line.id] = line_discounts

        # redistribute the discount to the lines
        # when discount_base == 'sale_order'
        for entry in grouped_discounts.values():
            match, pct = entry['sale_discount']._calculate_discount(
                lines=entry['lines'])
            if not match:
                continue
            for line in entry['lines']:
                if line.id not in line_updates:
                    line_updates[line.id] = [(entry['sale_discount'], pct)]
                else:
                    line_updates[line.id] += [(entry['sale_discount'], pct)]

        line_vals = []
        for line_id, line_discounts in line_updates.iteritems():
            pct_sum = 0.0
            exclusives = [x for x in line_discounts if x[0].exclusive]
            if exclusives:
                exclusives.sort(key=lambda x: x[0].sequence)
                line_discounts = [exclusives[0]]
            for disc in line_discounts:
                pct_sum += disc[1]
            pct_sum = min(pct_sum, 100.0)
            line_vals.append([1, line_id, {'discount': pct_sum}])

        vals = {}
        ctx = dict(self._context, discount_calc=True)
        if line_updates:
            vals['order_line'] = line_vals
            self.with_context(ctx).write(vals)

        vals = {}
        total_discount_amount = 0.0
        for line in self.order_line:
            base_amount = line.price_unit * line.product_uom_qty
            discount_pct = line.discount
            total_discount_amount += base_amount * discount_pct / 100.0
        if not self.currency_id.is_zero(
                self.discount_amount - total_discount_amount):
            vals['discount_amount'] = total_discount_amount
        if not self.currency_id.is_zero(
                self.discount_base_amount - total_base_amount):
            vals['discount_base_amount'] = total_base_amount
        if vals:
            self.with_context(ctx).write(vals)
