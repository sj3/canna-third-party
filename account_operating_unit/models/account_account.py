# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import fields, models
from openerp.addons.operating_unit.models import ou_model


class AccountAccount(ou_model.OUModel):
    _inherit = "account.account"

    operating_unit_id = fields.Many2one(
        comodel_name='operating.unit',
        string='Default Operating Unit',
        default=lambda self:
        self.env['res.users'].operating_unit_default_get(self._uid))
