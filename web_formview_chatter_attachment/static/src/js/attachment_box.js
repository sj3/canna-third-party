/* Copyright 2009-2024 Noviat (www.noviat.com) */

odoo.define("web_formview_chatter_attachment.AttachmentBox", function (require) {
    "use strict";

    var AttachmentBox = require('mail.AttachmentBox');

    AttachmentBox.include({

        init: function (parent, record, attachments) {
            this._super.apply(this, arguments);
            this.options = parent.options;
        },

        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.options.readonly) {
                    self.$(".o_upload_attachments_button").hide();
                    self.$(".o_attachment_delete_cross").hide();
                }
            });
        },

    });
});
