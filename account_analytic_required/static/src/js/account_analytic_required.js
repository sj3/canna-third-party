/*
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2015 Noviat nv/sa (www.noviat.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
*/
openerp.account_analytic_required = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliation.include({

        init: function(parent, context) {
            var self = this;
            this._super.apply(this, arguments);
            this.model_account = new instance.web.Model("account.account");
            this.map_analytic_policy = {};
        },

        start: function() {
            var tmp = this._super.apply(this, arguments);
            var self = this;

            maps = [];
            maps.push(self.model_account
                .query(['id', 'analytic_policy'])
                .filter([['type', 'not in', ['view', 'consolidation', 'closed']]])
                .all().then(function(data) {
                    _.each(data, function(o) {
                        self.map_analytic_policy[o.id] = o.analytic_policy;
                        });
                })
            );
            return $.when(tmp, maps);
        },

    });

    instance.web.account.bankStatementReconciliationLine.include({

        init: function(parent, context) {
            var self = this;
            this._super.apply(this, arguments);
            this.map_analytic_policy = this.getParent().map_analytic_policy;
        },

        formCreateInputChanged: function(elt, val) {
            var self = this;
            this._super.apply(this, arguments);
            if (elt === self.account_id_field) {
                if (self.map_analytic_policy[elt.get('value')] === 'always') {
                    this.analytic_account_id_field.modifiers = {'required': true, 'readonly': false};
                    if (! this.analytic_account_id_field.get('value')) {
                        self.$(".button_ok").text("OK").removeClass("oe_highlight").attr("disabled", "disabled");
                    };
                } else {
                    this.analytic_account_id_field.modifiers = undefined;
                    if (self.map_analytic_policy[elt.get('value')] === 'never') {
                       this.analytic_account_id_field.set('value', false);
                       this.analytic_account_id_field.modifiers = {'readonly': true};
                       self.balanceChanged();
                       };
                };
                this.analytic_account_id_field.field_manager.do_show();
            };
            if (elt === self.analytic_account_id_field) {
                if (self.analytic_account_id_field.modifiers && self.analytic_account_id_field.modifiers['required']) {
                    if (self.analytic_account_id_field.get('value')) {
                        self.balanceChanged();
                    } else {
                        self.$(".button_ok").text("OK").removeClass("oe_highlight").attr("disabled", "disabled");
                    };
                };
            };
        },

    });

};
