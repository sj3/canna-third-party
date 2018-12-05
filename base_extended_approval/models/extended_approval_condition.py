# -*- coding: utf-8 -*-
from openerp import api, fields, models
from openerp.tools import safe_eval


class ExtendedApprovalCondition(models.Model):
    _name = 'extended.approval.condition'

    name = fields.Char(
        string="Name",
        required=True)

    condition_type = fields.Selection(
        string="Type",
        required=True,
        selection="_get_condition_types")

    domain = fields.Char(
        string="Domain expression",
        size=512)

    @api.model
    def _get_condition_types(self):
        return [
            ('always', 'No condition'),
            ('domain', 'Domain condition')
        ]

    def is_applicable(self, record):
        return getattr(
            self, '_is_applicable_' + self.condition_type)(
                record)

    def _is_applicable_always(self, record):
        return True

    def _is_applicable_domain(self, record):
        return record.search(
            [('id', 'in', record._ids)]
            + safe_eval(self.domain) if self.domain else []
        )
