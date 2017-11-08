# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def button_cancel(self):
        if self.period_id.state == 'done':
                raise UserError(_(
                    "You can not cancel entries in a closed period"))
        return super(AccountMove, self).button_cancel()
