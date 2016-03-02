# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# @ 2016 Onestein BV
# - André Schenkels
# @ 2016 Noviat
# - Luc de Meyer
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tools.translate import _
from openerp import api, fields, models
from openerp.exceptions import Warning

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))

    @api.model
    def create(self, vals, check=True):
        if vals.get('move_id', False):
            move = self.env['account.move'].browse(vals['move_id'])
            if move.operating_unit_id:
                vals['operating_unit_id'] = move.operating_unit_id.id
        return super(AccountMoveLine, self).create(vals, check=check)

    @api.model
    def _query_get(self, obj='l'):
        query = super(AccountMoveLine, self)._query_get(obj=obj)
        if self.env.context.get('operating_unit_ids', False):
            operating_unit_ids = self.env.context.get('operating_unit_ids')
            query += 'AND ' + obj + '.operating_unit_id in (%s)' % (
                ','.join(map(str, operating_unit_ids)))
        return query

    @api.one
    @api.constrains('operating_unit_id', 'company_id')
    def _check_company_operating_unit(self):
        if self.company_id and self.operating_unit_id and \
                self.company_id != self.operating_unit_id.company_id:
            raise Warning(_('Configuration error!\nThe Company in the\
            Move Line and in the Operating Unit must be the same.'))

    @api.one
    @api.constrains('operating_unit_id', 'move_id')
    def _check_move_operating_unit(self):
            if (
                self.move_id and self.move_id.operating_unit_id and
                self.operating_unit_id and
                self.move_id.operating_unit_id != self.operating_unit_id
            ):
                raise Warning(_('Configuration error!\nThe Operating Unit in\
                the Move Line and in the Move must be the same.'))