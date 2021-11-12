odoo.define('web.set_user_home_action', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Menu = require("web.Menu");

var _t = core._t;

Menu.include({
    events: _.extend({}, Menu.prototype.events, {
         "click .set_as_user_home_action_manager": "set_user_home_action",
    }),
    set_user_home_action: function() {
        var self = this;
        var actionID = false;
        if(this.current_secondary_menu){
            actionID = parseInt(this.menu_id_to_action_id(this.current_secondary_menu));
        } else {
            actionID = parseInt(this.menu_id_to_action_id(this.current_primary_menu));
        }
        ajax.jsonRpc("/set_user_home_action",'call', {'actionID':actionID}).then(function() {
            self.do_notify(_t("Home Action Configuration"), _t("You have successfully configured Home Action."));
        });
    },
});

});
