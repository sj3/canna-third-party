# Copyright (C) Noviat 2024
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ExtendedApprovalMixin(models.TransientModel):
    _name = "wizard.change.approval.flow"
    _description = "Change approval flow"

    ref_model = fields.Reference(selection=lambda self: self._select_target_model(), default=lambda self: self._default_ref_model())

    approval_flow_id = fields.Many2one(comodel_name="extended.approval.flow")

    @api.model
    def _default_ref_model(self):
        return self.env[self.env.context.get('active_model')].browse(self.env.context.get('active_id'))
    
    def _select_target_model(self):
        models = self.env ['ir.model']. search ([])
        return [(model.model, model.name) for model in models]

    @api.onchange('ref_model')
    def onchange_ref_model(self):
        self.approval_flow_id = self.ref_model.current_step.flow_id
        return {'domain': {'approval_flow_id': [('id', 'in', self.ref_model._get_applicable_approval_flows().mapped('id'))]}}
    
    def do_change_approval_flow(self):
        self.ref_model.ea_cancel_approval()
        self.ref_model.write({
            'current_step': self.approval_flow_id.steps[0].id
        })
        return {"type": "ir.actions.act_window_close"}
    
        
   
