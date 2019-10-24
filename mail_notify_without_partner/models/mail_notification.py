from openerp import api, fields, models


class MailNotification(models.Model):
    _inherit = 'mail.notification'

    @api.multi
    def _notify_email(self, message_id, force_send=False, user_signature=True):
        res = super(MailNotification, self)._notify_email(message_id, force_send=force_send,
                                                          user_signature=user_signature)
        email_to = self.env.context.get('email_to')
        if email_to:
            message = self.env['mail.message'].sudo().search([('id', '=', message_id)])
            if message.type == 'comment' and message.subtype_id == self.env.ref('mail.mt_comment'):
                references = message.parent_id.message_id if message.parent_id else False
                for email in email_to:
                    mail_values = {
                        'mail_message_id': message.id,
                        'auto_delete': self.env.context.get('mail_auto_delete', True),
                        'mail_server_id': self.env.context.get('mail_server_id', False),
                        'body_html': message.body,
                        'email_to': email,
                        'references': references,
                    }
                    self.env['mail.mail'].create(mail_values)
        return res
