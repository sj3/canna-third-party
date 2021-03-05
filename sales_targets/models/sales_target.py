# Copyright (C) 2021-TODAY SerpentCS Pvt. Ltd. (<http://www.serpentcs.com>).

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class SalesTarget(models.Model):
    _name = "sales.target"
    _inherit = ["extended.approval.workflow.mixin", "mail.thread"]
    _description = "Sales Target"
    _rec_name = 'date_range_id'

    # signal to start the approval flow
    workflow_signal = "draft"
    # value of the workflow_state_field for the approval
    workflow_state = "approval"
    # fallback state when the approval is rejected
    workflow_start_state = "draft"

    date_range_id = fields.Many2one(
        "date.range", string="Sales Target", copy=False, readonly=True,
        states={'draft': [('readonly', False)]})
    date_start = fields.Date(
        related='date_range_id.date_start', string="Date From")
    date_end = fields.Date(related='date_range_id.date_end', string="Date To")
    product_category_id = fields.Many2one(
        'product.category', string="Product Category", copy=False,
        readonly=True, states={'draft': [('readonly', False)]})
    currency_id = fields.Many2one(
        'res.currency', string='Currency', readonly=True,
        default=lambda self: self.env.company.currency_id)
    target_in_currency = fields.Monetary(
        string='Target in Currency', copy=False, readonly=True,
        states={'draft': [('readonly', False)]})
    target_in_liter= fields.Float(
        string='Target in Liter', copy=False, readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection([
        ('draft', 'Draft'),('approval', 'Approval'), ('confirmed', 'Confirmed')
        ], string='Status', copy=False, default='draft', readonly=True,
        tracking=True)

    @api.model
    def create(self, vals):
        res = super(SalesTarget, self).create(vals)
        res.approve_step()
        return res

    @api.constrains('date_start', 'date_end')
    def _check_target_dates(self):
        for targets in self:
            if targets.date_end and targets.date_start and \
                    targets.date_end < targets.date_start:
                raise ValidationError(
                    _('Date to cannot be earlier than the Date from.'))

    def target_approval(self):
        for target in self:
            target.state = 'approval'

    def target_confirm(self):
        for target in self:
            target.state = 'confirmed'

    def target_set_to_draft(self):
        self.ea_cancel_approval()
        self.state = "draft"
        return {}
