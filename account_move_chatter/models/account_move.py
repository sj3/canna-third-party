# Copyright 2009-2019 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["account.move", "mail.thread"]

    state = fields.Selection(track_visibility="onchange")
