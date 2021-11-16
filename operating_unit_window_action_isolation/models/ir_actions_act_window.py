from odoo import SUPERUSER_ID, models
from odoo.tools.safe_eval import safe_eval


class IrActionsActWindow(models.Model):
    _inherit = "ir.actions.act_window"

    def read(self, fields=None, load="_classic_read"):
        act = res = super().read(fields=fields, load=load)

        if isinstance(res, list):
            act = res[0]

        if (
            self.env.uid != SUPERUSER_ID
            and act.get("res_model", False)
            and act["res_model"] in self.env
            and "operating_unit_id" in self.env[act["res_model"]]._fields
        ):

            user_ou = (
                self.env["res.users"]
                .browse(self.env.uid)
                .sudo()
                .read(["default_operating_unit_id"])[0]["default_operating_unit_id"]
            )

            if not user_ou:
                return res

            if act.get("domain", False):
                try:
                    act_ctx = safe_eval(act.get("domain", ""))
                    act_ctx.append(("operating_unit_id", "in", [False, user_ou[0]]))
                    act["domain"] = str(act_ctx)
                except ValueError:
                    pass
            else:
                act["domain"] = str([("operating_unit_id", "in", [False, user_ou[0]])])

        return res
