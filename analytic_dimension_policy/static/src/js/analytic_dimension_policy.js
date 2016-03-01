/*
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
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
openerp.analytic_dimension_policy = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliation.include({

        init: function(parent, context) {
            this._super.apply(this, arguments);
            this.model_account = new instance.web.Model("account.account");
            this.map_analytic_dimension_policy = {};
            var required_dict = {};
            _.each(this.create_form_fields, function(field) {                
                if (field['required']) {
                    required_dict[field['id']] = false;
                    };
                });
            /* 
            this.required_fields_set is used to check if all required fields 
            are filled in before showing the 'Ok' button on a line
            */
            this.required_fields_set = required_dict;
        },

        start: function() {
            var tmp = this._super.apply(this, arguments);
            var self = this;
            maps = [];
            maps.push(this.model_account
                .query(['id', 'analytic_dimension_policy'])
                .filter([['type', 'not in', ['view', 'consolidation', 'closed']]])
                .all().then(function(data) {
                    _.each(data, function(o) {
                        self.map_analytic_dimension_policy[o.id] = o.analytic_dimension_policy;
                        });
                })
            );
            return $.when(tmp, maps);
        },

    });

    instance.web.account.bankStatementReconciliationLine.include({

        init: function(parent, context) {
            this._super.apply(this, arguments);
            this.map_analytic_dimension_policy = this.getParent().map_analytic_dimension_policy;
            this.required_fields_set = this.getParent().required_fields_set;
            },

        UpdateRequiredFields: function(elt) {
            if (elt.get('value')) {
                this.required_fields_set[elt.name] = true;
            } else {
                this.required_fields_set[elt.name] = false;
            };
            var balanceChangedFlag = this.CheckRequiredFields(elt);
            if (balanceChangedFlag) {
                this.balanceChanged();      
            } else {
                this.$(".button_ok").text("OK").removeClass("oe_highlight").attr("disabled", "disabled");
            };
        },
        
        CheckRequiredFields: function() {
            var flag = _.every(this.required_fields_set);
            return flag;
        },

    });

};