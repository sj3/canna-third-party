# Copyright 2018 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import xlwt

from openerp import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def action_users_groups_analysis_xls(self):
        cell_color = xlwt.easyxf('pattern: pattern solid, fore_colour 0x11')
        wbs = xlwt.Workbook()
        ws1 = wbs.add_sheet('Users Groups')

        col_counter = 2
        row_counter = 0
        group_map = {}
        for user in self:
            col_counter += 1
            ws1.write(0, col_counter, user.login)
            for group in user.groups_id:
                group_name = group.name
                if group.category_id:
                    group_name = group.category_id.name + '/' + group_name
                if group.id not in group_map:
                    row_counter += 1
                    group_map[group.id] = row_counter
                    ws1.write(row_counter, 0, 'id=' + str(group.id))
                    ws1.write(row_counter, 1, group_name)
                    module_name = self.sudo().env['ir.model.data'].search([
                        ('model', '=', 'res.groups'),
                        ('res_id', '=', group.id)
                    ]).module
                    if module_name:
                        ws1.write(row_counter, 2, module_name)
                ws1.write(group_map[group.id], col_counter, 'Y', cell_color)

        ws2 = wbs.add_sheet('Other Groups')
        group_list = list(group_map.keys())
        row_counter = 0
        groups = self.sudo().env['res.groups'].search([
            ('id', 'not in', group_list)
        ])
        for group in groups:
            row_counter += 1
            group_name = group.name
            if group.category_id:
                group_name = group.category_id.name + '/' + group_name
            ws2.write(row_counter, 0, group.id)
            ws2.write(row_counter, 1, group_name)
            module_name = self.sudo().env['ir.model.data'].search([
                ('model', '=', 'res.groups'),
                ('res_id', '=', group.id)
            ]).module
            if module_name:
                ws2.write(row_counter, 2, module_name)

        return wbs
