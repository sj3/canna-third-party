# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from StringIO import StringIO

from openerp import api, fields, models


class UserGroupAnalysisXls(models.TransientModel):
    _name = "user.group.analysis.xls"
    _description = "User Group Analysis Xls"

    xlsfile = fields.Binary('xls file', readonly=True)
    xlsfile_name = fields.Char('Filename')
    file_type = fields.Char(default='xls')

    @api.multi
    def button_generate(self):
        self.ensure_one()

        user_ids = self._context.get('active_ids', [])
        users = self.env['res.users'].browse(user_ids)
        wbs = users.action_users_groups_analysis_xls()

        fp = StringIO()
        wbs.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        self.xlsfile = base64.b64encode(data)
        self.xlsfile_name = self._cr.dbname + '_' + fields.Datetime.now() + '.xls'

        res_id = self.env['ir.model.data'].get_object_reference('user_group_analysis_xls', 'user_group_analysis_xls_form')[1]

        return {
            'name': 'User Group Analysis Xls',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': 'user.group.analysis.xls',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
