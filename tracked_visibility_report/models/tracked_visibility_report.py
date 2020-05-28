# -*- coding: utf-8 -*-
# Copyright 2019-2020 Onestein.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openerp import api, fields, models
from openerp.addons.mail.mail_thread import mail_thread


class TrackVisibilityReport(models.Model):
    """Report on fields which are marked by track_visibility."""
    _name = "tracked.visibility.report"
    _inherit = "mail.message"
    _description = "Audit Changed Fields"
    _rec_name = "record_name"
    message_id = fields.Many2one(string="Message", comodel_name="mail.message")


message_track_orig = mail_thread.message_track
message_post_orig = mail_thread.message_post


@api.cr_uid_ids_context
def message_track(self, cr, uid, ids, tracked_fields, initial_values,
                  context=None):
    """Override to inject context to notify message_post that the passed
    message is tracked.
    """
    if context is None:
        context = {}

    context2 = dict(context, auditable=True)
    res_status = message_track_orig(self, cr, uid, ids, tracked_fields,
                                    initial_values, context2)
    return res_status


@api.cr_uid_ids_context
def message_post(
    self, cr, uid, thread_id, body="", subject=None, type="notification",
    subtype=None, parent_id=False, attachments=None, context=None,
    content_subtype="html", **kwargs
):
    """Override to create a new tracked.visibility.report and pass values from
    mail.message to it.
    """
    if context is None:
        context = {}
    msg_id = message_post_orig(
        self, cr, uid, thread_id, body=body, subject=subject, type=type,
        subtype=subtype, parent_id=parent_id, attachments=attachments,
        context=context, content_subtype=content_subtype, **kwargs
    )
    mail_message = self.pool.get("mail.message").browse(cr, 1, msg_id)
    if context.get("auditable"):
        vals = {
            "message_id": msg_id,
            "body": mail_message.body,
            "model": mail_message.model,
            "res_id": mail_message.res_id,
            "record_name": mail_message.record_name or mail_message.model,
        }
        if self.pool.get("tracked.visibility.report"):
            self.pool["tracked.visibility.report"].create(cr, uid, vals,
                                                          context=context)
    return msg_id


mail_thread.message_track = message_track
mail_thread.message_post = message_post
