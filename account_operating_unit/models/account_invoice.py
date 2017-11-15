# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid),
        help="This operating unit will be defaulted in the invoice lines.")

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not vals.get('operating_unit_id') \
                and self._context.get('operating_unit_id'):
            vals['operating_unit_id'] = self._context['operating_unit_id']
        return super(AccountInvoice, self).create(vals)

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if 'operating_unit_id' in line:
            res['operating_unit_id'] = line['operating_unit_id']
        return res
