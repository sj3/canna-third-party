# Copyright (C) Onestein 2019-2020
# Copyright (C) Noviat 2020
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ExtendedApprovalMixin(models.AbstractModel):
    _name = "extended.approval.mixin"
    _description = "Mixin class for extended approval"

    next_approver = fields.Many2many(
        comodel_name="res.groups",
        related="current_step.group_ids",
        readonly=True,
        string="Next Approver Role(s)",
    )

    current_step = fields.Many2one(
        comodel_name="extended.approval.step",
        copy=False,
        string="Current Approval Step",
    )
    flow_name = fields.Char(related="current_step.flow_id.name", string="Flow")

    approval_history_ids = fields.One2many(
        comodel_name="extended.approval.history",
        compute="_compute_history_ids",
        readonly=True,
        copy=False,
        string="Approval History",
    )

    approval_allowed = fields.Boolean(
        string="Approval allowed",
        compute="_compute_approval_allowed",
        search="_search_approval_allowed",
        help="This option is set if you are allowed to approve.",
    )

    def _compute_approval_allowed(self):
        for rec in self:
            rec.approval_allowed = (
                not rec.next_approver
                or any([a in self.env.user.groups_id for a in rec.next_approver])
            ) and rec._get_applicable_approval_flow()

    @api.model
    def _search_approval_allowed(self, operator, value):
        if operator in ["=", "!="]:
            return [
                (
                    "current_step.group_ids",
                    "in" if operator == "=" else "not in",
                    self.env.user.mapped("groups_id.trans_implied_ids.id")
                    + self.env.user.mapped("groups_id.id"),
                )
            ]
        else:
            raise UserError(_("Unsupported operand for search !"))

    def _compute_history_ids(self):
        for rec in self:
            rec.approval_history_ids = self.env["extended.approval.history"].search(
                [("source", "=", "{},{}".format(rec._name, rec.id))]
            )

    @api.model
    def recompute_all_next_approvers(self):
        if hasattr(self, "ea_state_field") and hasattr(self, "ea_start_state"):
            self.search(
                [(self.ea_state_field, "in", [self.ea_start_state])]
            )._recompute_next_approvers()

    def ea_retry_approval(self):
        for rec in self:
            step = rec._get_next_approval_step()
            if step != rec.current_step:
                rec.with_context(approval_flow_update=True).current_step = step

    def _recompute_next_approvers(self):
        for rec in self:
            completed = (
                self.env["extended.approval.history"]
                .search([("source", "=", "{},{}".format(rec._name, rec.id))])
                .mapped("step_id")
            )
            if not completed:
                # re-evaluate current step, but not during approval ?
                step = rec._get_next_approval_step()
                if step and step != rec.current_step:
                    rec.with_context(approval_flow_update=True).current_step = step

    def write(self, values):
        r = super().write(values)

        if "approval_flow_update" not in self._context:
            self._recompute_next_approvers()

        return r

    def _get_applicable_approval_flow(self):
        self.ensure_one()

        flows = self.env["extended.approval.flow"].search(
            [("model", "=", self._name)], order="sequence"
        )
        for c_flow in flows:
            if self.search(
                [("id", "in", self._ids)] + safe_eval(c_flow.domain)
                if c_flow.domain
                else []
            ):
                return c_flow
        return False

    def _get_next_approval_step(self):
        self.ensure_one()

        flow = self._get_applicable_approval_flow()
        if not flow:
            return False

        # computed field approval_history_ids is not refreshed, so search
        completed = (
            self.env["extended.approval.history"]
            .search([("source", "=", "{},{}".format(self._name, self.id))])
            .mapped("step_id")
        )
        for step in flow.steps:
            if step not in completed and step.is_applicable(self):
                return step

        return False

    def approve_step(self):
        """Attempt current approval step.

        Returns False if approval is completed
        """
        self.ensure_one()

        step = self._get_next_approval_step()
        if not step:
            self.current_step = step
            return False

        prev_step = False
        while step and step != prev_step:
            prev_step = step
            if any([g in self.env.user.groups_id for g in step.group_ids]):
                self.env["extended.approval.history"].create(
                    {
                        "approver_id": self.env.user.id,
                        "source": "{},{}".format(self._name, self.id),
                        "step_id": step.id,
                    }
                )

                # move to next step
                step = self._get_next_approval_step()

        self.current_step = step
        if step:
            return {
                "warning": {
                    "title": _("Extended approval required"),
                    "message": _("Approval by {role} required").format(
                        role=", ".join(step.group_ids.mapped("full_name"))
                    ),
                }
            }

        return False

    def ea_cancel_approval(self):
        self.approval_history_ids.sudo().write({"active": False})
        self.write({"current_step": False})
        return {}

    def ea_abort_approval(self):
        self.ea_cancel_approval()
        return {}

    def show_approval_group_users(self):
        a_user_ids = self.next_approver.mapped("users.id")
        ptree = self.env.ref("base.view_users_tree")
        action = {
            "name": _("Approval Group Users"),
            "type": "ir.actions.act_window",
            "res_model": "res.users",
            "view_type": "form",
            "view_mode": "tree",
            "view_id": ptree.id,
            "domain": [("id", "in", a_user_ids)],
            "context": self._context,
        }
        return action

    def _get_approval_user(self):
        self.ensure_one()
        history = self.env["extended.approval.history"].search(
            [("source", "=", "{},{}".format(self._name, self.id))],
            order="date desc, id desc",
        )
        for rec in history:
            if rec.step_id.use_sudo:
                return rec.approver_id

        return False
