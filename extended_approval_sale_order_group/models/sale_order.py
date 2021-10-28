# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_applicable_approval_flow(self):
        if self.sale_order_group_id:
            return False

        return super()._get_applicable_approval_flow()
