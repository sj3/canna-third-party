# -*- coding: utf-8 -*-
# Copyright 2019 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.exceptions import Warning as UserError

import logging
_logger = logging.getLogger(__name__)


class AccountTaxCode(models.Model):
    _inherit = 'account.tax.code'

    def move_line_domain_for_chart_of_taxes_row(
            self, cr, uid, tax_code_id, context):
        """
        The logic of this method in the OpusVL module is wrong since
        the domain that is returned is based upon dates
        in stead of accountng periods.
        In Odoo 8.0 all tax declarations have to be based
        upon accounting periods since there is no 'accounting_date'yet
        on e.g. supplier invoices.

        Remark:
        this change has been implemented assuming that a cutoff day is always
        aligend with a fiscal period.

        TODO: make PR to OpusVL


        tax_code_id: int
        context: must contain at least keys:
          date_to: string in format %Y-%m-%d
          date_from: string in format %Y-%m-%d
          company_id: int
          vat: 'all', 'posted' or 'unposted'
          state: 'all' or 'posted' (required journal entry states)
        """
        # This method is and should remain a pure function on tax_code_id and
        # context.
        # We accept cr, uid purely to make the javascript openerp.Model call
        # happy
        env = api.Environment(cr, uid, context)

        def param_or_user_error(ctx, key):
            try:
                return ctx[key]
            except KeyError:
                headline = "Missing parameters for chart of taxes."
                _logger.exception("%s  See exception." % (headline,))
                raise UserError(
                    "%s\n"
                    "This is usually caused by refreshing the webpage from a"
                    " previous chart of taxes report." % (headline,)
                )

        entry_state_filter = param_or_user_error(context, 'state')
        assert entry_state_filter in ('all', 'posted'), "Invalid state_filter"
        wanted_journal_entry_states = (
            ('draft', 'posted')
            if entry_state_filter == 'all'
            else ('posted',)
        )
        date_from = param_or_user_error(context, 'date_from')
        date_to = param_or_user_error(context, 'date_to')
        company_id = param_or_user_error(context, 'company_id')
        periods = env['account.period'].search(
            [('date_start', '>=', date_from),
             ('date_stop', '<=', date_to),
             ('company_id', '=', company_id),
             ('special', '=', False)],
        )
        if date_from not in periods.mapped('date_start'):
            raise UserError(
                "Date 'From' not aligned with fiscal period start date.")
        if date_to not in periods.mapped('date_stop'):
            raise UserError(
                "Date 'To' not aligned with fiscal period stop date.")
        domain = [
            ('state', '!=', 'draft'),
            ('move_id.state', 'in', wanted_journal_entry_states),
            ('tax_code_id', 'child_of', tax_code_id),
            ('company_id', '=', company_id),
            ('period_id', 'in', periods.ids)
        ]
        vat_clauses = {
            'posted': [('vat', '=', True)],
            'unposted': [('vat', '=', False)],
            'all': [],
        }
        vat_filter = param_or_user_error(context, 'vat')
        domain += vat_clauses[vat_filter]
        return domain

    def _move_line_ids_for_chart_of_taxes_row(
            self, cr, uid, tax_code_id, context):
        """
        Bypass of small bug.
        Without this fix the tax code list view is not
        accessible.
        TODO: make PR to fix module of OPUSVL
        """
        if not context.get('state'):
            return []
        else:
            return super(AccountTaxCode, self
                         )._move_line_ids_for_chart_of_taxes_row(
                             cr, uid, tax_code_id, context)
