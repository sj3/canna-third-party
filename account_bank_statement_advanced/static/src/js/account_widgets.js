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
openerp.account_bank_statement_advanced = function (instance) {

    instance.web.account.bankStatementReconciliation.include({

        start: function() {
            var tmp = this._super.apply(this, arguments);
            var self = this;

            /*
            function copied from standard addons with replacement of ['account_id', '=', false] by ['amount', '!=', 0.0] to filter
            TODO : make PR to standard addons
            */
            var lines_filter = [['journal_entry_id', '=', false], ['amount', '!=', 0.0]];
            //var lines_filter = [['journal_entry_id', '=', false], ['account_id', '=', false]];
            if (self.statement_ids && self.statement_ids.length > 0) {
                lines_filter.push(['statement_id', 'in', self.statement_ids]);
            };
            var deferred_promises = [];
            deferred_promises.push(self.model_bank_statement_line
                .query(['id'])
                .filter(lines_filter)
                .all().then(function (data) {
                    self.st_lines = _(data).map(function(o){ return o.id });
                })
            );
            return $.when(tmp, deferred_promises);
        },

    });

    instance.web.account.bankStatementReconciliationLine.include({

        createFormWidgets: function() {
            /*
            The standard bank statements allows to select only partners for which the
            customer or supplier flag is set. 
            We remove this limitation so that we can reconcile with all open entries.
            */
            this._super.apply(this, arguments);
            this['change_partner_field'].field.domain = [['parent_id','=',false]];
            this['change_partner_field'].field_manager.do_show();
        },

    });

};
