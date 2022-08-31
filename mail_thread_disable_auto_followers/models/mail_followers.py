# Copyright 2009-2022 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailFollowers(models.AbstractModel):
    _inherit = "mail.followers"

    def _get_subscription_data(self, doc_data, pids, cids, include_pshare=False):
        res = super()._get_subscription_data(
            doc_data, pids, cids, include_pshare=include_pshare
        )
        daf_models = self.env.context.get("mail_thread_disable_auto_followers", [])
        if (
            self.env.context.get("mail_create_nosubscribe")
            and self.env.context.get("active_model") in daf_models
        ):
            res_out = []
            for fid, rid, _pid, cid, subtype_ids, pshare in res:
                res_out.append((fid, rid, None, cid, subtype_ids, pshare))
            return res_out
        else:
            return res
