# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models, _
from openerp.exceptions import Warning as UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def button_cancel(self):
        for move in self:
            for move_line in move.line_id:
                st = move_line.statement_id
                if st and st.state == 'confirm':
                    raise UserError(
                        _("Operation not allowed ! "
                          "\nYou cannot unpost an Accounting Entry "
                          "that is linked to a Confirmed Bank Statement."))
        return super(AccountMove, self).button_cancel()
