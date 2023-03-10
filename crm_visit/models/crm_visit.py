# Copyright (c) 2015 Onestein BV (www.onestein.eu).
# Copyright (C) 2020-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CrmVisit(models.Model):
    _name = "crm.visit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Visits"
    _order = "date desc"

    name = fields.Char(string="Number", readonly=True)
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("planned", "Appointment"),
            ("visited", "Needs Report"),
            ("cancel", "Cancelled"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
        readonly=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Employee",
        required=True,
        default=lambda self: self.env.user,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Datetime(
        string="Visit Datetime",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)], "visited": [("readonly", False)]},
    )
    duration = fields.Integer(
        string="Duration",
        readonly=True,
        help="Estimated duration of the " "visit in minutes",
        states={"draft": [("readonly", False)], "visited": [("readonly", False)]},
    )
    visit_reason = fields.Many2one(
        comodel_name="crm.visit.reason",
        string="Reason",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    visit_reason_details = fields.Text(
        string="Purpose", readonly=True, states={"draft": [("readonly", False)]}
    )
    visit_feeling = fields.Many2one(
        comodel_name="crm.visit.feeling",
        string="Feeling",
        readonly=True,
        states={"visited": [("readonly", False)]},
    )
    report = fields.Html(
        string="Report",
        readonly=True,
        required=False,
        states={"visited": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )

    @api.model
    def create(self, vals):
        """
        This creates a new visitor.report object and adds any information
        that is placed in readonly fields.
        Readonly fields don't get send to the server, so we retrieve
        those fields from previous visits.
        """
        vals["name"] = self.env["ir.sequence"].next_by_code("crm.visit")
        return super().create(vals)

    def unlink(self):
        for visit in self:
            if visit.state != "draft":
                raise UserError(_("Only visits in state 'draft'" " can be deleted. "))
        return super().unlink()

    def action_confirm(self):
        self.state = "planned"

    def action_edit(self):
        self.state = "draft"

    def action_process(self):
        self.state = "visited"

    def action_done(self):
        if not self.visit_feeling or not self.report:
            raise UserError(_("Fill out the report and visit feeling."))
        self.state = "done"

    def action_correct(self):
        self.state = "visited"
