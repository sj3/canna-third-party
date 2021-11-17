# Copyright 2009-2021 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_abstract import (
    ReportXlsxAbstract,
)

_render = ReportXlsxAbstract._render


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def _report_xlsx_fields(self):
        res = super()._report_xlsx_fields()
        ix = res.index("account")
        res.insert(ix + 1, "operating_unit_name")
        return res

    @api.model
    def _report_xlsx_template(self):
        update = super()._report_xlsx_template()
        update.update(
            {
                "operating_unit_name": {
                    "header": {"value": _("Operating Unit")},
                    "lines": {
                        "value": _render(
                            "line.operating_unit_id "
                            "and line.operating_unit_id.name or ''"
                        )
                    },
                    "width": 25,
                }
            }
        )
        return update
