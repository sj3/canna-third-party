odoo.define('web.UserMenuCustomised', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var UserMenu = require('web.UserMenu');
var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;

    UserMenu.include({
        _onMenuAboutOdoo: function() {
            var self = this;
            ajax.jsonRpc("/web/webclient/version_info",'call', {}).then(function(res) {
                var $help = $(QWeb.render("UserMenu.about", {version_info: res}));
                $help.find('a.oe_activate_debug_mode').click(function (e) {
                    e.preventDefault();
                    window.location = $.param.querystring( window.location.href, 'debug');
                });
                new Dialog(this, {
                    size: 'medium',
                    dialogClass: 'oe_act_window',
                    title: _t("About"),
                    $content: $help
                }).open();
            });
        },
    });
});
