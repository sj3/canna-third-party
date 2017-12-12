from openerp import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        related="product_tmpl_id.operating_unit_id",
    )
