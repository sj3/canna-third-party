# Copyright (C) Startx 2021
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ExtendedApprovalMethodMixin(models.AbstractModel):
    """
    This mixin will trigger the extended approval on the call
    of the named method.
    """

    _name = "extended.approval.method.mixin"
    _inherit = "extended.approval.mixin"
    _description = "Mixin class for extended approval button"

    ea_method_name = "button_confirm"
    ea_flow_check = "before"

    def _register_hook(self):
        def _ea_approve(self, *args, **kwargs):
            if self.ea_flow_check == "before":
                approve = self.approve_step()
                if approve:
                    return approve

            r = _ea_approve.origin(self, *args, **kwargs)

            if self.ea_flow_check != "before":
                approve = self.approve_step()
                if approve:
                    # rollback all changes made in the transaction so far
                    self.env._cr.rollback()
                    return self.approve_step()

            return r

        ea_patched = getattr(self, "ea_patched", None)
        if not ea_patched and getattr(self, self.ea_method_name, False):
            self._patch_method(self.ea_method_name, _ea_approve)
            self.ea_patched = True

        return super()._register_hook()
