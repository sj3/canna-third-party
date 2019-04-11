# -*- coding: utf-8 -*-
from openerp import api, fields, models
from .extended_approval_mixin import ExtendedApprovalMixin


class ExtendedApprovalFlow(models.Model):
    _name = 'extended.approval.flow'
    _inherit = ['extended.approval.config.mixin']
    _order = 'sequence'

    name = fields.Char(
        string="Name")

    sequence = fields.Integer(
        string='Priority',
        default=10)

    model = fields.Selection(
        string="Model name",
        selection="_get_extended_approval_models")

    domain = fields.Char(
        string="Domain for this flow")

    signal_name = fields.Char(
        string="Signal",
        help="If specified this workflow signal will "
        "start the extended approval.")

    steps = fields.One2many(
        comodel_name='extended.approval.step',
        inverse_name='flow_id',
        string="Steps")

    @api.multi
    def get_applicable_models(self):
        return [self.model]

    @api.model
    def _get_extended_approval_models(self):

        def _get_subclasses(cls):
            for sc in cls.__subclasses__():
                for ssc in _get_subclasses(sc):
                    yield ssc
                yield sc

        return [
            (x, x) for x in
            list(set([
                c._name for c in
                _get_subclasses(ExtendedApprovalMixin)
                if issubclass(c, models.Model)
                and hasattr(c, '_name')]))]
