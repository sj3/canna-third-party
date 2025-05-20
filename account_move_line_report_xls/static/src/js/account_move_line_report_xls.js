/*
# Copyright 2025 Noviat.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/

odoo.define("account_move_line_report_xls.account_move_line_report_xls", function(
    require
) {
    "use strict";

    var Sidebar = require("web.Sidebar");

    Sidebar.include({
        _onItemActionClicked: function(item) {
            var xml_id =
                "account_move_line_report_xls.action_account_move_line_xlsx_all";
            if (item.action && item.action.xml_id === xml_id) {
                var self = this;
                this.trigger_up("sidebar_data_asked", {
                    callback: function(env) {
                        var activeIdsContext = {
                            active_model: env.model,
                        };
                        if (env.domain) {
                            activeIdsContext.active_domain = env.domain;
                        }
                        self._rpc({
                            model: "account.move.line",
                            method: "aml_export_all",
                            kwargs: {
                                domain: env.domain,
                                context: env.context,
                            },
                        }).then(function(result) {
                            result.context = env.context;
                            result.flags = result.flags || {};
                            result.flags.new_window = true;
                            self.do_action(result, {
                                on_close: function() {
                                    self.trigger_up("reload");
                                },
                            });
                        });
                    },
                });
            } else {
                this._super(item);
            }
        },
    });
});
