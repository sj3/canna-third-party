# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    def _accrual_hashcode_fields(self, entry):
        res = super(AccountInvoice, self)._accrual_hashcode_fields(entry)
        res['operating_unit_id'] = entry.get('operating_unit_id', False)
        return res

    def _update_accrual_move_line_vals(self, entry):
        super(AccountInvoice, self)._update_accrual_move_line_vals(entry)
        if entry.get('origin'):
            origin = entry['origin']
            if isinstance(origin, models.Model) and origin.operating_unit_id:
                entry['operating_unit_id'] = origin.operating_unit_id.id
