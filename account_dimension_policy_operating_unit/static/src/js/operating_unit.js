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
openerp.account_operating_unit = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;

    instance.web.account.bankStatementReconciliation.include({

        init: function(parent, context) {
            var self = this;
            this._super.apply(this, arguments);

            this.create_form_fields['operating_unit_id'] = {
                id: 'operating_unit_id',
                index: 5,
                label: _t("Operating Unit"),
                required: true,
                corresponding_property: 'operating_unit_id',
                tabindex: 15,
                constructor: instance.web.form.FieldMany2One,
                field_properties: {
                    relation: 'operating.unit',
                    string: _t("Operating Unit"),
                    type: 'many2one',
                },
            };
            this.required_fields_set['operating_unit_id'] = false;
        },

    });

    instance.web.account.bankStatementReconciliationLine.include({

        formCreateInputChanged: function(elt, val) {
            var self = this;
            this._super.apply(this, arguments);
            if (elt === self.operating_unit_id_field) {
                self.UpdateRequiredFields(elt);
            };            
        },

        prepareCreatedMoveLineForPersisting: function(line) {
            var self = this;
            var dict = this._super.apply(this, arguments);
            if (line.operating_unit_id) dict['operating_unit_id'] = line.operating_unit_id;
            return dict;
        },

    });

};
