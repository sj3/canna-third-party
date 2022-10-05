# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020-2022
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ExtendedApprovalStateFieldMixin(models.AbstractModel):
    """
    This mixin defines the state field used for the extended approval.
    """

    _name = "extended.approval.state_field.mixin"
    _description = "Mixin class for extended approval state field"

    # field used to track the approval flow. Must be a selection field
    ea_state_field = "state"
    # value of the workflow_state_field for the extended approval
    ea_state = "extended_approval"
    # fallback state when the approval is rejected
    ea_start_state = "draft"

    @api.model
    def _setup_complete(self):
        """
        Insert extra  approval state in the workflow_state_field selection just before
        the workflow_signal or at the end if there is no workflow_signal is the
        selection
        """
        super()._setup_complete()
        field = self.fields_get([self.ea_state_field]).get(self.ea_state_field)
        if field:
            try:
                state_names = [t[0] for t in field["selection"]]
                if self.ea_state not in state_names:
                    if self.ea_start_state in state_names:
                        field["selection"].insert(
                            state_names.index(self.ea_start_state) + 1,
                            (self.ea_state, "Approval"),
                        )
                    else:
                        field["selection"].append((self.ea_state, "Approval"))
            except TypeError:
                # probably a callable selection attribute
                # TODO: decorated callable
                pass

    def ea_abort_approval(self):
        super().ea_abort_approval()
        self.write({self.ea_state_field: self.ea_start_state})
        return {}

    def approve_step(self):
        r = super().approve_step()
        if r is False:
            # reset state to start_state after approval, because
            # eg ocb / purchase button_confirm checks it
            self.write({self.ea_state_field: self.ea_start_state})
        else:
            self.write({self.ea_state_field: self.ea_state})

        return r
