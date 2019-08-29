# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for so in self:
            if so.sale_order_group_id:
                for so2 in so.sale_order_group_id.sale_order_ids:
                    so2.compute_discount()
        return res