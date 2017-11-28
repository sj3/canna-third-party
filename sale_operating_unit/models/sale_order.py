# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# © 2017 Noviat
# © 2017 Onestein
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))

    @api.one
    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        if self.company_id and self.operating_unit_id and\
                self.company_id != self.operating_unit_id.company_id:
            raise UserError(_('Configuration error!\nThe Company in the\
            Sales Order and in the Operating Unit must be the same.'))

    @api.onchange('partner_invoice_id')
    def _onchange_partner_invoice_id(self):
        cp = self.partner_invoice_id.commercial_partner_id
        if cp.operating_unit_id:
            self.operating_unit_id = cp.operating_unit_id

    @api.model
    def _make_invoice(self, order, lines):
        inv_id = super(SaleOrder, self)._make_invoice(order, lines)
        invoice = self.env['account.invoice'].browse(inv_id)
        invoice.write({'operating_unit_id': order.operating_unit_id.id})
        return inv_id


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        related='order_id.operating_unit_id',
        string='Operating Unit',
        readonly=True)
