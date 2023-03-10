# Copyright 2009-2020 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import csv
import io
import os

from odoo import _, api, fields, models
from odoo.modules.module import ad_paths

CN_file_year = "2019"
CN_file_delimiter = ";"


class IntrastatInstaller(models.TransientModel):
    _name = "intrastat.installer"
    _inherit = "res.config.installer"
    _description = "Intrastat Installer"

    CN_file = fields.Selection(
        selection="_selection_CN_file",
        string="Intrastat Code File",
        required=True,
        default=lambda self: self._default_CN_file(),
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self._default_company_id(),
        required=True,
        string="Company",
    )

    @api.model
    def _selection_CN_file(self):
        return [
            (CN_file_year + "_en", CN_file_year + " " + _("English")),
            (CN_file_year + "_fr", CN_file_year + " " + _("French")),
            (CN_file_year + "_nl", CN_file_year + " " + _("Dutch")),
        ]

    @api.model
    def _default_CN_file(self):
        lang = self.env.user.lang[:2]
        if lang not in ["fr", "nl"]:
            lang = "en"
        return CN_file_year + "_" + lang

    @api.model
    def _default_company_id(self):
        return self.env.company

    @api.model
    def _load_code(self, row):
        code_obj = self.env["hs.code"]
        vals = {"description": row["description"]}
        cn_unit_id = row["unit_id"]
        if cn_unit_id:
            cn_unit_ref = "intrastat_product." + cn_unit_id
            cn_unit = self.env.ref(cn_unit_ref)
            vals["intrastat_unit_id"] = cn_unit.id
        cn_code = row["code"]
        cn_code_i = self.cn_lookup.get(cn_code)
        if isinstance(cn_code_i, int):
            self.cn_codes[cn_code_i].write(vals)
        else:
            vals["local_code"] = cn_code
            code_obj.create(vals)

    def execute(self):
        res = super().execute()
        company = self.company_id
        if self.company_id.country_id.code not in ("BE", "be"):
            return res

        # set company defaults
        module = __name__.split("addons.")[1].split(".")[0]
        transaction = self.env.ref("%s.intrastat_transaction_11" % module)
        if not company.intrastat_transaction_out_invoice:
            company.intrastat_transaction_out_invoice = transaction
        if not company.intrastat_transaction_out_refund:
            company.intrastat_transaction_out_refund = transaction
        if not company.intrastat_transaction_in_invoice:
            company.intrastat_transaction_in_invoice = transaction
        if not company.intrastat_transaction_in_refund:
            company.intrastat_transaction_in_refund = transaction

        # Set correct company_id on intrastat transactions.
        # Installation of this module under OdooBot will
        # set the company_id to 1 in stead of company that
        # needs the Belgian Intrastat Declaration.
        # TODO: make OCA PR for intrastat_product to make
        # shared intrastat transactions the default behaviour
        self.env.cr.execute(
            """
        SELECT imd.res_id FROM ir_model_data imd
        JOIN intrastat_transaction it ON imd.res_id=it.id
        WHERE imd.module=%s AND imd.model='intrastat.transaction'
          AND it.company_id IS NOT NULL
          AND it.company_id != %s
            """,
            (module, self.company_id.id),
        )
        trans_ids = [x[0] for x in self.env.cr.fetchall()]
        if trans_ids:
            self.env.cr.execute(
                """
            UPDATE intrastat_transaction
            SET company_id = %s
            WHERE id IN %s
                """,
                (self.company_id.id, tuple(trans_ids)),
            )

        # load intrastat_codes
        self.cn_codes = self.env["hs.code"].search([])
        self.cn_lookup = {}
        for i, c in enumerate(self.cn_codes):
            self.cn_lookup[c.local_code] = i
        for adp in ad_paths:
            module_path = adp + os.sep + module
            if os.path.isdir(module_path):
                break
        CN_fn = self.CN_file + "_intrastat_codes.csv"
        CN_fqn = module_path + os.sep + "static/data" + os.sep + CN_fn
        with io.open(CN_fqn, mode="r", encoding="Windows-1252") as CN_file:
            cn_codes = csv.DictReader(CN_file, delimiter=CN_file_delimiter)
            for row in cn_codes:
                self._load_code(row)
        return res
