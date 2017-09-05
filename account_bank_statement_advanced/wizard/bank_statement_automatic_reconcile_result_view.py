# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import fields, models


class BankStatementAutomaticReconcileResultView(models.TransientModel):
    """
    Transient Model to display Automatic Reconcile results
    """
    _name = 'bank.statement.automatic.reconcile.result.view'

    note = fields.Text(
        string='Notes', readonly=True,
        default=lambda self: self._context.get('note'))
