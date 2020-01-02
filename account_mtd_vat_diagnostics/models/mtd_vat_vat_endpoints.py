# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.exceptions import Warning as UserError
from openerp.addons.account_mtd_vat.hmrc_vat import Box
from openerp.addons.account_mtd_vat.dictutils import \
    map_keys, restrict_with_fill_values

import logging
_logger = logging.getLogger(__name__)


class MtdVatVatEndpoints(models.Model):
    _inherit = 'mtd_vat.vat_endpoints'

    offline_calc = fields.Boolean(string="Calculate VAT Offline")

    def _get_periods(self):
        """
        The logic in the account_mtd_vat module handles the lookup
        of periods incorrectly.Hence we replace this logic.
        The 'replaced' logic assumes that the from/to dates
        are aligned with fiscal periods.

        For the manual calc we also do not take into account the
        'previous period' flag.

        TODO: make PR to OpusVL (and check if assumption on periods
        versus dates is correct)
        """
        periods = self.env['account.period'].search([
            ('date_start', '>=', self.date_from),
            ('date_stop', '<=', self.date_to),
            ('company_id', '=', self.company_id.id),
            ('special', '=', False),
        ])
        return periods

    @api.multi
    def action_calc_offline(self, *args):
        """
        offline calc to run at any time
        - accounting period can be open or closed
        - account.move state should be posted
        """
        retrieve_vat_codes = self.env['account.tax.code'].search([
            ('code', 'in', list(Box.all_box_codes())),
            ('company_id', '=', self.company_id.id)
        ])

        periods = self._get_periods()
        move_state = 'posted'
        where = " AND line.period_id IN %s AND move.state = %s "
        where_params = (tuple(periods.ids), move_state)
        sums_for_tax_codes = retrieve_vat_codes._sum(
            name='', args=None, context={},
            where=where, where_params=where_params)

        def tax_code_id_to_box_code(tax_code_id):
            return retrieve_vat_codes.filtered(
                lambda c: c.id == tax_code_id).code

        # _sum_period doesn't always return all boxes, and the ones it does
        #  are account.tax.code ids not the box codes themselves
        base_box_sums = restrict_with_fill_values(
            map_keys(tax_code_id_to_box_code, sums_for_tax_codes),
            wanted_keys=(Box.all_box_codes() - Box.computed_box_codes()),
            fill_value=0,
        )
        box_values = Box.compute_all(base_box_sums)
        field_box_map = {
            'vat_due_sales_submit': Box.VAT_DUE_SALES,
            'vat_due_acquisitions_submit': Box.VAT_DUE_ACQUISITIONS,
            'total_vat_due_submit': Box.TOTAL_VAT_DUE,
            'vat_reclaimed_submit': Box.VAT_RECLAIMED_ON_INPUTS,
            'net_vat_due_submit': Box.NET_VAT_DUE,
            'total_value_sales_submit': Box.TOTAL_VALUE_SALES,
            'total_value_purchase_submit': Box.TOTAL_VALUE_PURCHASES,
            'total_value_goods_supplied_submit':
                Box.TOTAL_VALUE_GOODS_SUPPLIED,
            'total_acquisitions_submit': Box.TOTAL_VALUE_ACQUISITIONS,
        }
        self.update({
            field: box_values[boxcode]
            for (field, boxcode) in field_box_map.items()
        })
