# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2013-2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, orm


class account_move_line(orm.Model):
    _inherit = "account.move.line"

    def _absolute_balance(self, cr, uid, ids, name, arg, context=None):
        cr.execute(
            "SELECT id, abs(debit-credit) "
            "FROM account_move_line WHERE id IN %s",
            (tuple(ids),))
        return dict(cr.fetchall())

    def _signed_balance(self, cr, uid, ids, name, arg, context=None):
        cr.execute(
            "SELECT id, debit-credit "
            "FROM account_move_line WHERE id IN %s",
            (tuple(ids),))
        return dict(cr.fetchall())

    _columns = {
        'absolute_balance': fields.function(
            _absolute_balance,
            string='Absolute Amount', store=True,
            help="Absolute Amount in Company Currency"),
        'signed_balance': fields.function(
            _signed_balance,
            string='Balance', store=True,
            help="Balance in Company Currency"),
    }
