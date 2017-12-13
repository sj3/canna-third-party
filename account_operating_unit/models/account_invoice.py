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
        help="This operating unit will be defaulted in the invoice lines.")

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        p = self.env['res.partner'].browse(partner_id)
        cp = p.commercial_partner_id
        res['value']['operating_unit_id'] = cp.operating_unit_id.id
        return res

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
        else:
            if line.get('type') == 'dest' and self.operating_unit_id:
                res['operating_unit_id'] = self.operating_unit_id.id
        return res

    @api.multi
    def action_move_create(self):
        res = super(AccountInvoice, self).action_move_create()
        for inv in self:
            inv.move_id.operating_unit_id = inv.operating_unit_id
        return res
