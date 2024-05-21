# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models, registry
from odoo.exceptions import UserError


class ExtendedApprovalWorkflowMixin(models.AbstractModel):
    """
    The Odoo workflow mechanism is replaced by an interception of the write method
    in the object when the workflow_state_field change.
    """

    _name = "extended.approval.workflow.mixin"
    _inherit = "extended.approval.state.field.mixin"
    _description = "Mixin class for extended approval workflow"

    # The state which, when written to ea_state_field triggers approval
    ea_signal = "confirmed"

    def write(self, vals):
        """
        The super is made after the approval process in order to have a
        clean mailthread trying to limit the conversion of multi write to multiple
        one-writes at most.
        """
        if self and self[0].ea_state_field in vals:
            wstate = vals.get(self[0].ea_state_field)
            if wstate == self[0].ea_signal:
                for rec in self:
                    with api.Environment.manage():
                        with registry(self.env.cr.dbname).cursor() as new_cr:
                            new_env = api.Environment(
                                new_cr, self.env.uid, self.env.context
                            )
                            new_rec = rec.with_env(new_env)
                            r = new_rec.approve_step()

                            if r is not False:
                                new_rec.write({rec.ea_state_field: rec.ea_state})
                                new_cr.commit()

                                # Must raise exception to abort transaction and undo
                                # changes in call stack.
                                raise UserError(
                                    r.get("warning", {}).get(
                                        "message",
                                        _(
                                            "You do not have the required "
                                            "access to approve!"
                                        ),
                                    )
                                )

                            new_cr.commit()
                    super(ExtendedApprovalWorkflowMixin, rec).write(vals)
                return True

        return super().write(vals)
