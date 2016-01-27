# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
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

from openerp import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    """
    This module adds fields to facilitate UI enforcement
    of analytic dimensions.
    """

    analytic_dimension_policy = fields.Selection(
        string='Policy for analytic dimension',
        related='account_id.analytic_dimension_policy', readonly=True)
    move_state = fields.Selection(
        string='Move State',
        related='move_id.state',
        default='draft',  # required for view attrs before object is created
        readonly=True)
