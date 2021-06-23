from openerp import api, models


class PaymentOrder(models.Model):
    _name = "payment.order"
    _inherit = ["payment.order", "extended.approval.workflow.mixin"]

    workflow_signal = "open"
    workflow_state = "extended_approval"

    @api.multi
    def action_cancel(self):
        self.cancel_approval()
        return super(PaymentOrder, self).action_cancel()
