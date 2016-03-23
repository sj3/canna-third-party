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

from openerp import api, models, _
from openerp.addons.report_xls.utils import _render


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _report_xls_fields(self):
        res = super(AccountMoveLine, self)._report_xls_fields()
        ix = res.index('account')
        res.insert(ix + 1, 'operating_unit_name')
        return res

    @api.model
    def _report_xls_template(self):
        update = super(AccountMoveLine, self).\
            _report_xls_template()
        update['operating_unit_name'] = {
            'header': [1, 25, 'text', _('Operating Unit')],
            'lines': [
                1, 0, 'text', _render(
                    "line.operating_unit_id and "
                    "line.operating_unit_id.name "
                    "or ''")]}
        return update
