# Copyright 2009-2022 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.safe_eval import safe_eval


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def send_mail(self, auto_commit=False):
        daf_models = safe_eval(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("mail_thread_disable_auto_followers")
            or "[]"
        )
        if self.env.context.get("active_model") in daf_models:
            self = self.with_context(
                dict(
                    self.env.context,
                    mail_create_nosubscribe=True,
                    mail_post_autofollow=False,
                )
            )
        return super().send_mail(auto_commit=auto_commit)
