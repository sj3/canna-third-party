/*
 ##############################################################################
 #
 #    Odoo, Open Source Management Solution
 #
 #    Copyright (c) 2009-2016 Noviat nv/sa (www.noviat.com).
 #    Copyright (c) 2009-2016 Onestein BV (www.onestein.eu).
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

openerp.account_dimension_policy_operating_unit = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliationLine.include({

        formCreateInputChanged: function(elt, val) {
            this._super.apply(this, arguments);
            if (elt === this.account_id_field) {
                if (this.map_analytic_dimension_policy[elt.get('value')] === 'always') {
                    this.operating_unit_id_field.modifiers = {'required': true, 'readonly': false};
                    if (! this.operating_unit_id_field.get('value')) {
                        this.required_fields_set['operating_unit_id'] = false;
                        this.$(".button_ok").text("OK").removeClass("oe_highlight").attr("disabled", "disabled");
                    };
                } else {
                    delete this.required_fields_set['operating_unit_id'];
                    if (this.map_analytic_dimension_policy[elt.get('value')] === 'never') {
                        this.operating_unit_id_field.set('value', false);
                        this.operating_unit_id_field.modifiers = {'required': false, 'readonly': true};
                    } else {
                        this.operating_unit_id_field.modifiers = {'required': false, 'readonly': false};
                    };
                };
                this.operating_unit_id_field.field_manager.do_show();
            };
            this.UpdateRequiredFields(elt);
        },

    });

};