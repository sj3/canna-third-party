# -*- coding: utf-8 -*-
# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from openerp import api, fields, models, _
from openerp.addons.report_xlsx_helpers.report.abstract_report_xlsx \
    import AbstractReportXlsx
from openerp.report import report_sxw
from openerp.tools.translate import translate
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

IR_TRANSLATION_NAME = 'l10n.nl.vat.intracom'


class l10nNlVatIntracom(models.TransientModel):
    _name = 'l10n.nl.vat.intracom'
    _inherit = 'l10n.nl.vat.common'
    _description = 'Intracom VAT Declaration'

    # result view fields
    client_ids = fields.One2many(
        comodel_name='l10n.nl.vat.intracom.client',
        inverse_name='intracom_id',
        string='Clients')

    @api.multi
    def generate_declaration(self):
        self.ensure_one()
        client_vals = self._get_client_vals()
        self.client_ids = [(0, 0, x) for x in client_vals]

        module = __name__.split('addons.')[1].split('.')[0]
        result_view = self.env.ref(
            '%s.%s_view_form_declaration' % (module, self._table))

        return {
            'name': _('Intracom VAT Declaration'),
            'res_id': self.id,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': self._name,
            'target': 'inline',
            'view_id': result_view.id,
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def create_xls(self):
        module = __name__.split('addons.')[1].split('.')[0]
        report_name = '%s.report_l10n_nl_vat_intracom_xlsx' % module
        report = {
            'type': 'ir.actions.report.xml',
            'report_type': 'xlsx',
            'report_name': report_name,
            'context': dict(self._context, xlsx_export=True),
            'datas': {'ids': [self.id]},
        }
        return report

    @api.multi
    def print_declaration(self):
        module = __name__.split('addons.')[1].split('.')[0]
        return self.env['report'].get_action(
            self, '%s.report_l10n_nl_vat_intracom' % module)

    def _get_client_vals(self):
        flds = ['partner_id', 'debit', 'credit']
        groupby = ['partner_id']

        aml_dom = self._get_move_line_date_domain()
        S_dom, L_dom, T_dom, O_dom = self._get_move_line_tax_domains()
        S_data = self.env['account.move.line'].read_group(
            aml_dom + S_dom, flds, groupby)
        for entry in S_data:
            entry['code'] = 'S'
        L_data = self.env['account.move.line'].read_group(
            aml_dom + L_dom, flds, groupby)
        for entry in L_data:
            entry['code'] = 'L'
        T_data = self.env['account.move.line'].read_group(
            aml_dom + T_dom, flds, groupby)
        for entry in T_data:
            entry['code'] = 'T'
        O_data = self.env['account.move.line'].read_group(
            aml_dom + O_dom, flds, groupby)
        for entry in O_data:
            entry['code'] = '-'

        records = {}
        for entry in S_data + L_data + T_data + O_data:
            partner = self.env['res.partner'].browse(entry['partner_id'][0])
            vat = self._normalise_vat(partner.vat)
            if vat in records:
                records[vat].append({
                    'partner_id': partner.id,
                    'name': partner.name,
                    'vat': vat,
                    'code': entry['code'],
                    'amount': entry['credit'] - entry['debit'],
                })
            else:
                records[vat] = [{
                    'partner_id': partner.id,
                    'name': partner.name,
                    'vat': vat,
                    'code': entry['code'],
                    'amount': entry['credit'] - entry['debit'],
                }]

        ic_vals = []
        for k in records:
            ic_vals += records[k]
        ic_vals.sort(key=lambda k: k['vat'])
        return ic_vals

    def _get_move_line_tax_domains(self):

        tax_code = '3b'

        tax_codes = self.env['account.tax.code'].search(
            [('code', '=', tax_code)])
        dom = [('tax_code_id', 'in', tax_codes.ids)]
        S_dom = dom + [('product_id.type', '=', 'service')]
        L_dom = dom + [('product_id.type', 'in', ['product', 'consu'])]
        O_dom = dom + [('product_id', '=', False)]

        tax_code = '3b-T'
        tax_codes = self.env['account.tax.code'].search(
            [('code', '=', tax_code)])
        T_dom = [('tax_code_id', 'in', tax_codes.ids)]

        return S_dom, L_dom, T_dom, O_dom

    def _get_intra_list(self):
        intra_list = {}
        for client in self.client_ids:
            vat = client.vat
            if vat == '-':
                raise UserError(_(
                    "Missing VAT number for partner '%s'")
                    % client.partner_id.name)
            key = '%s-%s' % (vat, client.code)
            if key in intra_list:
                intra_list[key]['amount'] += client.amount
            else:
                intra_list[key] = {
                    'vat': client.vat,
                    'code': client.code,
                    'amount': client.amount,
                }
        for k in intra_list.keys():
            if not intra_list[k]['amount']:
                del intra_list[k]
        return intra_list


class l10nNlVatIntracomClient(models.TransientModel):
    _name = 'l10n.nl.vat.intracom.client'

    intracom_id = fields.Many2one(
        comodel_name='l10n.nl.vat.intracom',
        string='Intracom VAT Declaration')
    partner_id = fields.Many2one(
        comodel_name='res.partner', readonly=1)
    vat = fields.Char(
        string='VAT Number', readonly=1)
    code = fields.Selection(
        selection=[('L', 'L'), ('S', 'S'), ('T', 'T'), ('-', '-')],
        readonly=1)
    amount = fields.Float(
        string='Amount',
        digits=dp.get_precision('Account'),
        readonly=1)
    currency_id = fields.Many2one(
        related='intracom_id.currency_id',
        readonly=1)

    @api.multi
    def view_move_lines(self):
        self.ensure_one()
        act_window = self.intracom_id._move_lines_act_window()
        aml_dom = self.intracom_id._get_move_line_date_domain()
        aml_dom += [('partner_id', '=', self.partner_id.id)]
        tax_doms = self.intracom_id._get_move_line_tax_domains()
        i = ['S', 'L', 'T', '-'].index(self.code)
        act_window['domain'] = aml_dom + tax_doms[i]
        return act_window


class l10nNlVatIntracomXlsx(AbstractReportXlsx):

    def _(self, src):
        lang = self.env.context.get('lang', 'en_US')
        val = translate(
            self.env.cr, IR_TRANSLATION_NAME, 'report', lang, src) or src
        return val

    def _get_ws_params(self, workbook, data, listing):

        col_specs = {
            'seq': {
                'header': {
                    'value': self._('Nr'),
                },
                'lines': {
                    'value': self._render("str(seq)"),
                },
                'width': 5,
            },
            'vat': {
                'header': {
                    'value': self._('VAT Number'),
                },
                'lines': {
                    'value': self._render("c.vat"),
                },
                'width': 18,
            },
            'partner': {
                'header': {
                    'value': self._('Partner'),
                },
                'lines': {
                    'value': self._render("c.partner_id.name"),
                },
                'width': 52,
            },
            'code': {
                'header': {
                    'value': self._('Code'),
                    'format': self.format_theader_yellow_center,
                },
                'lines': {
                    'value': self._render("c.code"),
                    'format': self.format_tcenter,
                },
                'width': 5,
            },
            'amount': {
                'header': {
                    'value': self._('Amount'),
                    'format': self.format_theader_yellow_right,
                },
                'lines': {
                    'value': self._render("c.amount"),
                    'format': self.format_tamount,
                },
                'totals': {
                    'type': 'formula',
                    'value': self._render("total_amount_formula"),
                    'format': self.format_theader_yellow_amount,
                },
                'width': 18,
            },
        }
        wanted_list = ['seq', 'vat', 'partner', 'code', 'amount']

        return [{
            'ws_name': 'vat_intra_%s' % listing.period,
            'generate_ws_method': '_generate_listing',
            'title': listing._description,
            'wanted_list': wanted_list,
            'col_specs': col_specs,
        }]

    def _generate_listing(self, workbook, ws, ws_params, data, listing):

        ws.set_portrait()
        ws.fit_to_pages(1, 0)
        ws.set_header(self.xls_headers['standard'])
        ws.set_footer(self.xls_footers['standard'])

        self._set_column_width(ws, ws_params)

        row_pos = 0
        row_pos = self._listing_title(ws, row_pos, ws_params, data, listing)
        row_pos = self._listing_info(ws, row_pos, ws_params, data, listing)
        row_pos = self._listing_lines(ws, row_pos, ws_params, data, listing)

    def _listing_title(self, ws, row_pos, ws_params, data, listing):
        return self._write_ws_title(ws, row_pos, ws_params)

    def _listing_info(self, ws, row_pos, ws_params, data, listing):
        ws.write_string(row_pos, 1, self._('Company') + ':',
                        self.format_left_bold)
        ws.write_string(row_pos, 2, listing.company_id.name)
        row_pos += 1
        ws.write_string(row_pos, 1, self._('VAT Number') + ':',
                        self.format_left_bold)
        ws.write_string(row_pos, 2, listing.company_id.vat or '-')
        row_pos += 1
        ws.write_string(row_pos, 1, self._('Period') + ':',
                        self.format_left_bold)
        ws.write_string(row_pos, 2, listing.period)
        return row_pos + 2

    def _listing_lines(self, ws, row_pos, ws_params, data, listing):

        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='header',
            default_format=self.format_theader_yellow)

        ws.freeze_panes(row_pos, 0)

        seq = 1
        row_pos_start = row_pos
        previous_client = False
        for c in listing.client_ids:
            if seq > 1:
                if c.vat == previous_client.vat:
                    seq -= 1
            row_pos = self._write_line(
                ws, row_pos, ws_params, col_specs_section='lines',
                render_space={'seq': seq, 'c': c},
                default_format=self.format_tleft)
            seq += 1
            previous_client = c

        amount_pos = ws_params['wanted_list'].index('amount')
        amount_start = self._rowcol_to_cell(row_pos_start, amount_pos)
        amount_stop = self._rowcol_to_cell(row_pos - 1, amount_pos)
        total_amount_formula = 'SUM(%s:%s)' % (amount_start, amount_stop)
        row_pos = self._write_line(
            ws, row_pos, ws_params, col_specs_section='totals',
            render_space={
                'total_amount_formula': total_amount_formula,
            },
            default_format=self.format_theader_yellow)

        return row_pos + 1


l10nNlVatIntracomXlsx(
    'report.l10n_nl_icp.report_l10n_nl_vat_intracom_xlsx',
    'l10n.nl.vat.intracom',
    parser=report_sxw.rml_parse)
