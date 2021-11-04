# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def approve_step(self):
        so_approval_flow = super()._get_applicable_approval_flow()
        if self.sale_order_group_id:
            if (
                so_approval_flow
                and not self.sale_order_group_id._get_applicable_approval_flow()
            ):
                raise UserError(
                    _(
                        "Configuration Error: No approval flow defined "
                        "on Sale Order Group."
                    )
                )
        return super().approve_step()

    def _get_applicable_approval_flow(self):
        if self.sale_order_group_id:
            return False

        return super()._get_applicable_approval_flow()
