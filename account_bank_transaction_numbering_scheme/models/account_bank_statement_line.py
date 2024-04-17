# Copyright 2009-2024 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountBankStatementLine(models.Model):
    _inherit = "account.bank.statement.line"

    def process_reconciliation(
        self, counterpart_aml_dicts=None, payment_aml_rec=None, new_aml_dicts=None
    ):
        """
        The standard process_reconciliation logic performs an update of the
        statement line sequence field but this logic does not work when the
        reconciliation order doesn't correspond with the line order.
        As a consequence we need to override this logic.

        Also for this reason we do not use _prepare_reconciliation_move()
        since that method is called after update of the sequence field.
        """
        if (
            not self.move_name
            and self.statement_id.journal_id.transaction_numbering == "statement"
        ):
            lines = self.statement_id.line_ids
            lines_done = lines.filtered(lambda r: r.move_name)
            lines_todo = lines - lines_done
            sequence = self.sequence
            sequences = [x.sequence for x in lines]
            seqs_done = [x.sequence for x in lines_done]
            if len(lines) != len(set(sequences)):
                # this is the case when a statement has been entered manually
                # without the use of the handle widget
                seqs = [x for x in range(1, len(lines) + 1)]
                seqs_free = [x for x in seqs if x not in seqs_done]
                index = 0
                for line in lines_todo:
                    if line == self:
                        break
                    else:
                        index += 1
                sequence = seqs_free[index]
            move_name = "{}/{}".format(
                self.statement_id.name, str(sequence).rjust(3, "0")
            )
            if move_name in lines.mapped("move_name"):
                # fix any remaining naming conflict via highest number
                sequence = max(seqs_done[-1], seqs_free[-1]) + 1
                move_name = "{}/{}".format(
                    self.statement_id.name, str(sequence).rjust(3, "0")
                )
            self.move_name = move_name
        res = super().process_reconciliation(
            counterpart_aml_dicts=counterpart_aml_dicts,
            payment_aml_rec=payment_aml_rec,
            new_aml_dicts=new_aml_dicts,
        )
        self.sequence = sequence
        return res
