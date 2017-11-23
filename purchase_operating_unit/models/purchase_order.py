# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# © 2015 Serpent Consulting Services Pvt. Ltd.
# © 2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def _get_picking_in(self):
        res = super(PurchaseOrder, self)._get_picking_in()
        type_obj = self.env['stock.picking.type']
        operating_unit = self.env['res.users'].operating_unit_default_get(
                self._uid)
        types = type_obj.search([('code', '=', 'incoming'),
                                 ('warehouse_id.operating_unit_id', '=',
                                  operating_unit.id)])
        if types:
            res = types[:1].id
        return res

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))

    requesting_operating_unit_id =fields.Many2one(
        comodel_name='operating.unit',
        string='Requesting Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))

    picking_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Deliver To',
        help="This will determine picking type "
             "of incoming shipment",
        required=True,
        states={'confirmed': [('readonly', True)],
        'approved': [('readonly', True)],
        'done': [('readonly', True)]},
        default=_get_picking_in)

    @api.one
    @api.constrains('operating_unit_id', 'picking_type_id')
    def _check_warehouse_operating_unit(self):
        picking_type = self.picking_type_id
        if picking_type:
            if picking_type.warehouse_id and\
                    picking_type.warehouse_id.operating_unit_id\
                    and self.operating_unit_id and\
                    picking_type.warehouse_id.operating_unit_id !=\
                    self.operating_unit_id:
                raise Warning(_('Configuration error!\nThe\
                Quotation / Purchase Order and the Warehouse of picking type\
                must belong to the same Operating Unit.'))

    @api.one
    @api.constrains('operating_unit_id', 'requesting_operating_unit_id',
                    'company_id')
    def _check_company_operating_unit(self):
        if self.company_id and self.operating_unit_id and\
                self.company_id != self.operating_unit_id.company_id:
            raise UserError(_(
                "Configuration error!\nThe Company in the "
                "Purchase Order and in the Operating Unit must be the same."
            ))

    # @api.onchange('partner_id')
    # def onchange_partner_id(self, partner_id):
    # TODO got the following error:
    # ValueError: "onchange_partner_id() takes exactly 2 arguments (6 given)" while evaluating
    # Probably because the onchange is driven
    # by an onchange declaration in the view, while the Odoo 8 API does not
    # use this. Reverted back to the old API.
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        res = super(PurchaseOrder, self).onchange_partner_id(
            cr, uid, ids, partner_id, context)
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id,
                                                      context)
        cp = partner.commercial_partner_id
        if cp.operating_unit_id:
            res['value']['operating_unit_id'] = cp.operating_unit_id
        return res

    @api.onchange('operating_unit_id')
    def _onchange_operating_unit_id(self):

        type_obj = self.env['stock.picking.type']
        if self.operating_unit_id:
            types = type_obj.search([('code', '=', 'incoming'),
                                     ('warehouse_id.operating_unit_id', '=',
                                      self.operating_unit_id.id)])
            if types:
                self.picking_type_id = types[:1]
            else:
                raise UserError(_(
                    "No Warehouse found with the Operating Unit "
                    "indicated in the Purchase Order!"))

    @api.one
    def action_picking_create(self):
        picking_obj = self.env['stock.picking']
        picking_id = super(PurchaseOrder, self).action_picking_create()
        picking = picking_obj.browse(picking_id)
        picking.operating_unit_id = self.operating_unit_id.id
        return picking_id

    @api.model
    def _prepare_invoice(self, order, line_ids):
        res = super(PurchaseOrder, self)._prepare_invoice(order, line_ids)
        if order.operating_unit_id:
            res['operating_unit_id'] = order.operating_unit_id.id
        return res

    @api.one
    @api.constrains('invoice_ids')
    def _check_invoice_ou(self):
        for po in self:
            for invoice in po.invoice_ids:
                if invoice.operating_unit_id != po.operating_unit_id:
                    raise UserError(_('The operating unit of the purchase order '
                                    'must be the same as in the '
                                    'associated invoices.'))


class PurchaseOrderLine(models.Model):
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
                if inv_line.invoice_id and \
                    inv_line.invoice_id.operating_unit_id != \
                        line.operating_unit_id:
                    raise UserError(_(
                        'The operating unit of the purchase order '
                        'must be the same as in the '
                        'associated invoices.'))
