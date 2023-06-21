# Copyright 2009-2023 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def button_update_prices(self):
        res = super().button_update_prices()
        self._update_discount()
        return res
