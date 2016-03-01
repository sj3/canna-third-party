# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Onestein BV (www.onestein.eu).
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

class CrmVisitReason(models.Model):
    _name = "crm.visit.reason"
    _description = "Visit reason"

    name = fields.Char(
        string="Reason",
        size=80,
        required=True,
        translate=True
    )

    company_id = fields.Many2one(
            comodel_name='res.company',
            string='Company',
            required=True,
            default=lambda self: self.env['res.company']._company_default_get('crm.visit.reason')
    )