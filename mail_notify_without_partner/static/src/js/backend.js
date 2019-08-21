openerp.mail_notify_without_partner = function (instance) {

    instance.mail.ThreadComposeMessage.include({
        check_recipient_partners: function () {
            var self = this;
            var recipients = _.filter(this.recipients, function (recipient) {
                return recipient.checked;
            });
            var recipients_to_find = _.filter(recipients, function (recipient) {
                return !recipient.partner_id;
            });
            // Cancel out showing the res.partner dialog
            if (recipients_to_find.length > 0) {
                return $.Deferred().resolve([]);
            }

            return this._super.apply(this, arguments);
        },

        do_send_message_post: function () {
            var recipients = _.filter(this.recipients, function (recipient) {
                return recipient.checked;
            });
            var recipients_to_find = _.filter(recipients, function (recipient) {
                return !recipient.partner_id;
            });
            if (recipients_to_find.length > 0) {
                this.parent_thread.context['email_to'] = _.map(recipients_to_find, function (item) {
                    return item.email_address;
                });
            }
            return this._super.apply(this, arguments);
        }
    });
}
