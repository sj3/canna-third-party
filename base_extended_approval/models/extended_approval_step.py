# -*- coding: utf-8 -*-
from openerp import fields, models


class ExtendedApprovalStep(models.Model):
    _name = 'extended.approval.step'

    _order = 'sequence'

    flow_id = fields.Many2one(
        comodel_name='extended.approval.flow',
        string="Extended Approval",
        required=True)

    sequence = fields.Integer(
        string='Priority',
        default=10)

    limit = fields.Float(
        string="Limit Amount")

    group_id = fields.Many2one(
        comodel_name='res.groups',
        string="Approver")

    def is_applicable(self, record):
        #return True

        # TODO: refactor to separte class
        return record.amount_total >= self.limit
