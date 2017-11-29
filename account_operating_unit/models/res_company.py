# -*- coding: utf-8 -*-
# © 2016-17 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Onestein BV
# © 2016-2017 Noviat
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.addons.operating_unit.models import ou_model
from openerp.exceptions import Warning as UserError


class ResCompany(ou_model.OUModel):
    _inherit = 'res.company'

    inter_ou_clearing_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Inter-operating unit clearing account')
    ou_is_self_balanced = fields.Boolean(
        string='Operating Units are self-balanced',
        help="Acomodel_namectivate if your company is required "
             "to generate a balancedbalance sheet for each operating unit.")

    @api.one
    @api.constrains('ou_is_self_balanced')
    def _inter_ou_clearing_acc_required(self):
        if self.ou_is_self_balanced and not \
                self.inter_ou_clearing_account_id:
            raise UserError(_(
                "Configuration error!\nPlease indicate an "
                "Inter-operating unit clearing account."))
