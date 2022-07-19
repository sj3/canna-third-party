# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    expense_line_ids = fields.One2many(states=None)
    journal_id = fields.Many2one(default=lambda self: self._default_journal_id())
    update_sheet_lines = fields.Boolean()

    @api.model
    def _default_journal_id(self):
        journal_ids = self.env["account.journal"]._search([("hr_expense", "=", True)])
        journal_id = journal_ids and journal_ids[0] or False
        return journal_id

    def action_sheet_move_create(self):
        res = super().action_sheet_move_create()
        self.write({"update_sheet_lines": False})
        return res

    def update_approved_lines(self):
        self.write({"update_sheet_lines": True})
        return True

    def update_approved_lines_done(self):
        self.write({"update_sheet_lines": False})
        return True
