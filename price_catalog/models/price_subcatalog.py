# Copyright 2020 Onestein B.V.
# Copyright 2020 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _


class PriceSubcatalog(models.Model):
    """Collects product prices valid for a certain period."""

    _name = "price.subcatalog"
    _description = "Price Subcatalog"
    _inherit = ["mail.thread"]
    _order = "start_date desc, sequence"

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(
        help="Open the and edit the Catalog to change the sequence using the "
        "handle widget, which is the first column of the Subcatalog list. The "
        "highest Subcatalog in the list will be scanned through for prices "
        "first. In other words: the lower the number on this field, the "
        "higher in the list Subcatalog will appear, which elevates the "
        "priority of prices to be looked up."
    )
    start_date = fields.Date(copy=False, default=fields.Date.today)
    end_date = fields.Date(copy=False)
    item_ids = fields.One2many(
        comodel_name="price.catalog.item", inverse_name="subcatalog_id"
    )
    catalog_id = fields.Many2one(
        comodel_name="price.catalog", string="Price Catalog", required=True
    )
    catalog_type = fields.Selection(related="catalog_id.catalog_type", store=True)
    catalog_type_filter = fields.Selection(
        selection=[
            ("sale", "Sale Price Catalog"),
            ("purchase", "Purchase Price Catalog"),
        ]
    )
    company_id = fields.Many2one(
        related="catalog_id.company_id", store=True, readonly=True, Index=True
    )

    def action_duplicate_subcatalog(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx['default_name'] = self.name
        ctx['default_catalog_id'] = self.catalog_id.id
        return {
            'name': _('Price Subcatalog'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'price.subcatalog',
            'view_id': self.env.ref('price_catalog.price_subcatalog_view_form').id,
            'context': ctx,
        }

    @api.constrains('start_date', 'end_date', 'catalog_id', 'active')
    def check_expired_price_overlap(self):
        for record in self:
            if record.start_date and record.catalog_id:
                # Check the empty end date Sub Catalogs
                empty_sub_cat_id = self.search([
                            ('id', '!=', record.id),
                            ('catalog_id', '=', record.catalog_id.id),
                            ('active', '=', True),
                            ('end_date', '=', False),
                            ('start_date', '<=', record.start_date)], limit=1, order='sequence desc')
                if empty_sub_cat_id:
                    raise ValidationError(_("First add an end date on previous Price Subcatalog '%s' ." % (empty_sub_cat_id.name)))
                # Check the overlapping Sub Catalogs
                date_domain = [('start_date', '<=', record.start_date)]
                if record.end_date:
                    date_domain = [('start_date', '<=', record.end_date)]
                    # check dates
                    if record.end_date < record.start_date:
                        raise ValidationError(_("End Date must be greater than the Start Date !"))
                overlap_sub_cat_id = self.search([
                        ('id', '!=', record.id),
                        ('catalog_id', '=', record.catalog_id.id),
                        ('active', '=', True),
                        ('end_date', '>=', record.start_date),
                        ] + date_domain, limit=1, order='sequence desc')
                if overlap_sub_cat_id:
                    raise ValidationError(_("You can not overlap the Price Subcatalog '%s' with date '%s' !" % (overlap_sub_cat_id.name, overlap_sub_cat_id.end_date)))
        return True
