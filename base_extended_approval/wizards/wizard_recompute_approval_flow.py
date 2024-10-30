# Copyright (C) Noviat 2024
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class WizardRecomputeApprovalFlow(models.TransientModel):
    _name = "wizard.recompute.approval.flow"
    _description = "Recompute approval flow"

    ref_model = fields.Selection(selection=lambda self: self.env["extended.approval.flow"]._get_extended_approval_models())
    domain = fields.Char()

    def do_recompute_approval_flow(self):
        self.ensure_one()
        if self.domain:
            self.env[self.ref_model].search(safe_eval(self.domain))._recompute_next_approvers()
        else:
            self.env[self.ref_model].recompute_all_next_approvers()

        return {"type": "ir.actions.act_window_close"}

