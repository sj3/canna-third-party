# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# © 2015 Serpent Consulting Services Pvt. Ltd.
# © 2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.addons.operating_unit.models import ou_model
from openerp.exceptions import Warning as UserError


class PurchaseOrder(ou_model.OUModel):
    _inherit = 'purchase.order'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))

    @api.multi
    def onchange_partner_id(self, partner_id):
        res = super(PurchaseOrder, self).onchange_partner_id(partner_id)
        partner = self.env['res.partner'].browse(partner_id)
        cp = partner.commercial_partner_id
        if cp.operating_unit_id:
            res['value']['operating_unit_id'] = cp.operating_unit_id
        return res

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):
        pass

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(PurchaseOrder, self)._prepare_invoice(order, line_ids)
        if order.operating_unit_id:
            res['operating_unit_id'] = order.operating_unit_id.id
        return res


class PurchaseOrderLine(ou_model.OUModel):
    _inherit = 'purchase.order.line'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        related='order_id.operating_unit_id',
        string='Operating Unit', readonly=True)

    @api.one
    @api.constrains('invoice_lines')
    def _check_invoice_ou(self):
        for line in self:
            for inv_line in line.invoice_lines:
                if inv_line.operating_unit_id and \
                    inv_line.operating_unit_id != \
                        line.operating_unit_id:
                    raise UserError(_(
                        'The operating unit of the purchase order '
                        'must be the same as in the '
                        'associated invoice lines.'))
