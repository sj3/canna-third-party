/* Copyright 2009-2024 Noviat (www.noviat.com) */

odoo.define("canna_kyc_document.FormRenderer", function (require) {
    "use strict";

    var Chatter = require("mail.Chatter");
    var FormRenderer = require("web.FormRenderer");
    var py_utils = require("web.py_utils");

    FormRenderer.include({
        _renderNode: function (node) {
            var self = this;
            if (
                node.tag === "div" &&
                node.attrs.class &&
                node.attrs.class.match(/\boe_chatter\b/)
            ) {
                var options =
                    node.attrs.options && py_utils.py_eval(node.attrs.options);
                if (options && options.render_attachments) {
                    if (!this.chatter) {
                        this.chatter = new Chatter(
                            this,
                            this.state,
                            this.mailFields,
                            {
                                isEditable: this.activeActions.edit,
                                viewType: "form",
                            }
                        );
                        var $temporaryParentDiv = $("<div>");
                        this.defs.push(
                            this.chatter
                                .appendTo($temporaryParentDiv)
                                .then(function () {
                                    self.chatter.$el.unwrap();
                                    self._handleAttributes(
                                        self.chatter.$el,
                                        node
                                    );
                                    console.log("self=", self);
                                    if (options.open_attachments) {
                                        self.chatter._onClickAttachmentButton();
                                    }
                                    if (options.hide_attachments_topbar) {
                                        self.chatter._$topbar.hide();
                                    }
                                })
                        );
                        return $temporaryParentDiv;
                    }
                    this.chatter.update(this.state);
                    return this.chatter.$el;
                }
            }
            return this._super.apply(this, arguments);
        },
    });
});
