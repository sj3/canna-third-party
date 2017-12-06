# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L.
# © 2015 Serpent Consulting Services Pvt. Ltd.
# © 2017 Noviat
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

    operating_unit_ids = fields.Many2many(
        comodel_name='operating.unit',
        relation='operating_unit_users_rel',
        column1='user_id',
        column2='poid',
        string='Operating Units',
        default=lambda self: self._get_operating_units())

    default_operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Default Operating Unit',
        default=lambda self: self._get_operating_unit())

    # selection field used by web_easy_switch_operating_unit module
    operating_unit = fields.Selection(
        selection=lambda self: self._selection_operating_unit(),
        string='Operating Unit')

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

    @api.model
    def _selection_operating_unit(self):
        user = self.browse(self._uid)
        # Allow admin to always pick all operating units.
        # This is required, because SELF_WRITEABLE_FIELDS uses 'uid = 1'
        if user.id == SUPERUSER_ID:
            selection = [(o.code, o.name) for o in
                    self.env['operating.unit'].search([])]
        else:
            selection = [(o.code, o.name) for o in
                         user.operating_unit_ids]
        return selection

    @api.multi
    def write(self, vals):
        if 'operating_unit' in vals:
            if vals.get('operating_unit'):
                operating_unit = self.env['operating.unit'].search(
                    [('code', '=', vals['operating_unit'])])
                vals['default_operating_unit_id'] = operating_unit.id
            else:
                vals['default_operating_unit_id'] = False
        return super(ResUsers, self).write(vals)
