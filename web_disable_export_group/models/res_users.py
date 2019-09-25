# -*- coding: utf-8 -*-
# Copyright Onestein (https://www.onestein.eu/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from openerp import api, models


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    @api.model
    def may_export(self, model):
        """Return True if user has group to export records of arg model."""
        if self.has_group('web_disable_export_group.group_export_data'):
            # User is allowed to export all data
            return True

        # Check if user is allowed to export data for the given model
        model_id = self.env['ir.model'].search([('model', '=', model)])
        assert len(model_id) == 1, "Expected exactly one model to export!"
        groups = model_id.export_group_ids

        if groups:
            return any(
                self.has_group(gxid) for gxid in groups.get_xml_id().values())
