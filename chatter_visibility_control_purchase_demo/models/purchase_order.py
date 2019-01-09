# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    amount_untaxed = fields.Float(
        track_visibility_groups='account.group_account_manager')
