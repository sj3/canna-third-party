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

import logging

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class ProcurementOrder(models.Model, CommonAccrual):
    _inherit = 'procurement.order'

    @api.model
    def _assign(self, procurement):
        res = super(ProcurementOrder, self)._assign(procurement)
        product = procurement.product_id
        supply_method = product.supply_method \
            or product.recursive_supply_method
        if not supply_method:
            return res
        rule = procurement.rule_id
        if (supply_method == 'stock' and rule.action == 'buy') \
                or (supply_method == 'buy' and rule.action == 'move'):
            raise UserError(_(
                "Configuration Error for Product '%s'."
                "\nSupply Method '%s' is not compatible with "
                "Procurement Rule Action '%s'")
                % (product.name, supply_method, rule.action))
        return res
