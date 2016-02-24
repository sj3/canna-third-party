# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# - Jordi Ballester Alomar
# @ 2016 Onestein BV
# - André Schenkels
# @ 2016 Noviat
# - Luc de Meyer
# © 2016 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    operating_unit_id = fields.Many2one('operating.unit', 'Operating Unit',
                                        default=lambda self:
                                        self.env['res.users'].
                                        operating_unit_default_get(self._uid))

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        if not vals.get('operating_unit_id') and self._context.get('operating_unit_id'):
            vals['operating_unit_id'] = self._context['operating_unit_id']
        return super(AccountInvoice, self).create(vals)

    @api.model
    def line_get_convert(self, line, part, date):
        res = super(AccountInvoice, self).line_get_convert(line, part, date)
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res

    @api.multi
    def _check_company_operating_unit(self):
        for pr in self.browse():
            if (
                pr.company_id and
                pr.operating_unit_id and
                pr.company_id != pr.operating_unit_id.company_id
            ):
                return False
        return True

    _constraints = [
        (_check_company_operating_unit,
         'The Company in the Invoice and in the Operating '
         'Unit must be the same.', ['operating_unit_id',
                                    'company_id'])]
