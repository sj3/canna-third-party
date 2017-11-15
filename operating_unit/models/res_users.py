# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, SUPERUSER_ID


class ResUsers(models.Model):
    _inherit = 'res.users'

    def __init__(self, pool, cr):
        init_res = super(ResUsers, self).__init__(pool, cr)
        # Duplicate list to avoid modifying the original reference.
        self.SELF_WRITEABLE_FIELDS = list(self.SELF_WRITEABLE_FIELDS)
        self.SELF_WRITEABLE_FIELDS.extend(
            ['operating_unit', 'default_operating_unit_id'])
        return init_res

    @api.model
    def operating_unit_default_get(self, uid2):
        if not uid2:
            uid2 = self._uid
        user = self.env['res.users'].browse(uid2)
        return user.default_operating_unit_id

    @api.model
    def _get_operating_unit(self):
        return self.operating_unit_default_get(self._uid)

    @api.model
    def _get_operating_units(self):
        return self._get_operating_unit()

    @api.multi
    def _operating_units_selection(self):
        user = self.browse(self._uid)
        # Allow admin to always pick all operating units.
        # This is required, because SELF_WRITEABLE_FIELDS uses 'uid = 1'
        if user.id == SUPERUSER_ID:
            return [(o.name, o.name) for o in
                    self.env['operating.unit'].search([])]
        return [(o.name, o.name) for o in
                user.operating_unit_ids]

    operating_unit_ids = fields.Many2many('operating.unit',
                                          'operating_unit_users_rel',
                                          'user_id', 'poid', 'Operating Units',
                                          default=_get_operating_units)
    default_operating_unit_id = fields.Many2one('operating.unit',
                                                'Default Operating Unit',
                                                default=_get_operating_unit)
    operating_unit = fields.Selection(_operating_units_selection,
                                      string='Operating Unit')

    @api.multi
    def write(self, vals):
        if vals.get('operating_unit'):
            operating_unit = self.env['operating.unit'].search(
                [('name', '=', vals['operating_unit'])])
            vals['default_operating_unit_id'] = operating_unit.id

        res = super(ResUsers, self).write(vals)
        return res
