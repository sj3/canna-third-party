# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models
from openerp.addons.operating_unit.models import ou_model


class AccountInvoiceLine(ou_model.OUModel):
    _inherit = 'account.invoice.line'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit')

    @api.model
    def create(self, vals):
        ail = super(AccountInvoiceLine, self).create(vals)
        if not vals.get('operating_unit_id') \
                and ail.invoice_id.operating_unit_id:
            ail.operating_unit_id = ail.invoice_id.operating_unit_id
        return ail

    @api.model
    def move_line_get_item(self, line):
        res = super(AccountInvoiceLine, self).move_line_get_item(line)
        res['operating_unit_id'] = line.operating_unit_id.id
        return res
