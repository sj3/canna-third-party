# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))

    @api.model
    def create(self, vals, **kwargs):
        if vals.get('move_id'):
            
            if 'operating_unit_id' not in vals:
                move = self.env['account.move'].browse(vals['move_id'])
                if move.operating_unit_id:
                    vals['operating_unit_id'] = move.operating_unit_id.id
        return super(AccountMoveLine, self).create(vals, **kwargs)

    @api.model
    def _query_get(self, obj='l'):
        query = super(AccountMoveLine, self)._query_get(obj=obj)
        if self.env.context.get('operating_unit_ids'):
            operating_unit_ids = self.env.context.get('operating_unit_ids')
            query += 'AND ' + obj + '.operating_unit_id in (%s)' % (
                ','.join(map(str, operating_unit_ids)))
        return query
