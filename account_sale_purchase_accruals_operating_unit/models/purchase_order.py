# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _accrual_hashcode_fields(self, entry):
        res = super(PurchaseOrder, self)._accrual_hashcode_fields(entry)
        res['operating_unit_id'] = entry['operating_unit_id'] or False,
        return res

    def _update_accrual_move_line_vals(self, entry):
        super(PurchaseOrder, self)._update_accrual_move_line_vals(entry)
        if entry.get('origin'):
            origin = entry['origin']
            if isinstance(origin, models.Model) and origin.operating_unit_id:
                entry['operating_unit_id'] = origin.operating_unit_id.id