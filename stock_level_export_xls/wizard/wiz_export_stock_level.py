# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class WizExportStockLevel(models.TransientModel):
    _name = 'wiz.export.stock.level'
    _description = 'Generate a stock level report for a given date'

    stock_level_date = fields.Datetime(
        string='Stock Level Date',
        help="Specify the Date & Time for the Stock Levels."
             "\nThe current stock level will be given if not specified.")
    categ_id = fields.Many2one(
        comodel_name='product.category',
        string='Product Category',
        help="Limit the export to the selected Product Category.")
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        help="Limit the export to the selected Warehouse.")
    location_id = fields.Many2one(
        comodel_name='stock.location',
        string='Location',
        domain=[('usage', '=', 'internal'), ('child_ids', '=', False)],
        help="Limit the export to the selected Location. ")
    product_select = fields.Selection([
        ('all', 'All Products'),
        ('select', 'Selected Products'),
        ], string='Products',
        default=lambda self: self._default_product_select())
    import_compatible = fields.Boolean(
        string='Import Compatible Export',
        help="Generate a file for use with the 'stock_level_import' module.")
    company_id = fields.Many2one(
        'res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get(
            'stock.inventory'))

    @api.model
    def _default_product_select(self):
        if self._context.get('active_model') in ['product.product',
                                                 'product.template']:
            return 'select'
        else:
            return 'all'

    @api.one
    @api.constrains('location_id')
    def _check_location_id(self):
        if self.location_id.child_ids:
            raise UserError(
                _("You cannot select a location which has Child Locations"))

    def _xls_export_domain(self):
        ctx = self._context
        domain = [
            ('type', 'in', ['product', 'consu']),
            '|', ('active', '!=', 'True'), ('active', '=', 'True'),
            '|', ('company_id', '=', self.company_id.id),
            ('company_id', '=', False)
        ]
        if self.categ_id:
            domain.append(('categ_id', 'child_of', self.categ_id.id))
        if self.product_select == 'select':
            if ctx.get('active_model') == 'product.product':
                domain.append(('id', 'in', ctx.get('active_ids')))
            elif ctx.get('active_model') == 'product.template':
                products = self.env['product.product'].search(
                    [('product_tmpl_id', 'in', ctx.get('active_ids'))])
                domain.append(('id', 'in', products._ids))
        return domain

    def _update_datas(self, datas):
        """
        Update datas when adding extra options to the wizard
        in inherited modules.
        """
        pass

    @api.multi
    def xls_export(self):
        self.ensure_one()
        warehouses = self.warehouse_id
        if not warehouses:
            warehouses = self.env['stock.warehouse'].search(
                [('company_id', '=', self.company_id.id)])
        warehouse_ids = warehouses._ids
        domain = self._xls_export_domain()
        products = self.env['product.product'].search(domain)
        if not products:
            raise UserError(
                _("No Data Available."),
                _("'\nNo records found for your selection !"))

        if self.location_id:
            warehouse_id = self.env['stock.location'].get_warehouse(
                self.location_id)
            if not warehouse_id:
                raise UserError(
                    _("No Warehouse defined for the selected "
                      "Stock Location "))
            warehouse_ids = [warehouse_id]

        datas = {
            'model': self._name,
            'stock_level_date':
                self.import_compatible
                and False or self.stock_level_date,
            'product_ids': products._ids,
            'category_id': self.categ_id.id,
            'warehouse_ids': warehouse_ids,
            'location_id': self.location_id.id,
            'product_select': self.product_select,
            'import_compatible': self.import_compatible,
            'company_id': self.company_id.id,
        }
        self._update_datas(datas)
        return {'type': 'ir.actions.report.xml',
                'report_name': 'stock.level.xls',
                'datas': datas}
