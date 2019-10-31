/******************************************************************************
    Based largely on: Web Easy Switch Company module for OpenERP
    Copyright (C) 2014 GRAP (http://www.grap.coop)
    @author Sylvain LE GAL (https://twitter.com/legalsylvain)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
******************************************************************************/

openerp.web_easy_switch_operating_unit = function (instance) {

    /***************************************************************************
    Create an new 'SwitchOperatingUnitWidget' widget that allow users to switch
    from a operating.unit to another more easily.
    ***************************************************************************/
    instance.web.SwitchOperatingUnitWidget = instance.web.Widget.extend({

        template:'web_easy_switch_operating_unit.SwitchOperatingUnitWidget',

        /***********************************************************************
        Overload section
        ***********************************************************************/

        /**
         * Overload 'init' function to initialize the values of the widget.
         */
        init: function(parent){
            this._super(parent);
            this.operating_units = [];
            this.current_operating_unit_id = 0;
            this.current_operating_unit_name = '';
        },

        /**
         * Overload 'start' function to load datas from DB.
         */
        start: function () {
            this._super();
            this._load_data();
        },

        /**
         * Overload 'renderElement' function to set events on operating.unit items.
         */
        renderElement: function() {
            var self = this;
            this._super();
            if (this.operating_units.length < 1) {
                this.$el.hide();
            }
            else{
                this.$el.show();
                this.$el.find('.easy_switch_operating_unit_operating_unit_item').on('click', function(ev) {
                    var operating_unit_id = $(ev.target).data("operating-unit-id");


                    if (operating_unit_id != self.current_operating_unit_id){
                        var func = '/web_easy_switch_operating_unit/switch/change_current_operating_unit';
                        var param = {'operating_unit_id': operating_unit_id}
                        self.rpc(func, param).done(function(res) {
                            window.location.reload();
                        });
                    }
                });
            }
        },


        /***********************************************************************
        Custom section
        ***********************************************************************/

        /**
         * helper function to load data from the server
         */
        _fetch: function(model, fields, domain, ctx){
            return new instance.web.Model(model).query(fields).filter(domain).context(ctx).all();
        },

        /**
         * - Load data of the operating_units allowed to the current users;
         * - Launch the rendering of the current widget;
         */
        _load_data: function(){
            var self = this;
            // Request for current users information
            this._fetch('res.users', ['default_operating_unit_id'], [['id', '=', this.session.uid]]).then(function (res_users) {
                if (res_users.length === 1) {

                    self.current_operating_unit_id = res_users[0].default_operating_unit_id[0];
                    self.current_operating_unit_name = res_users[0].default_operating_unit_id[1];

                    ou_logo = new instance.web.Model('operating.unit').query(["logo_topbar"]).filter([["id", "=", self.current_operating_unit_id]]).all();
                    // Do not show image if there is none
                    ou_logo.then(function (value) {
                        if (value.length > 0) {
                            self.logo_topbar = self.session.url(
                                '/web/binary/image', {
                                    model: 'operating.unit',
                                    field: 'logo_topbar',
                                    id: self.current_operating_unit_id
                                });
                        }
                    });

                    // Request for other operating_units
                    // We have to go through fields_view_get to emulate the
                    // exact (exotic) behavior of the user preferences form in
                    // fetching the allowed operating_units wrt record rules.
                    // Note: calling res.company.name_search with
                    //       user_preference=True in the context does
                    //       not work either.
                    new instance.web.Model('res.users').call('fields_view_get', { context: { 'form_view_ref': 'base.view_users_form_simple_modif' } }).then(function (res) {
                        var res_operating_unit = res.fields.operating_unit.selection;
                        for (var i = 0; i < res_operating_unit.length; i++) {
                            var logo_state;
                            if (res_operating_unit[i][0] == self.current_operating_unit_name) {
                                logo_state = '/web_easy_switch_operating_unit/static/description/selection-on.png';
                            }
                            else {
                                logo_state = '/web_easy_switch_operating_unit/static/description/selection-off.png';

                            }
                            self.operating_units.push({
                                id: res_operating_unit[i][0],
                                name: res_operating_unit[i][1],
                                logo_state: logo_state
                            });
                        }
                        // Update rendering
                        self.renderElement();
                    });

                };
            });
        },

    });

    /***************************************************************************
    Extend 'UserMenu' Widget to insert a 'Switchoperating.unitWidget' widget.
    ***************************************************************************/
    instance.web.UserMenu =  instance.web.UserMenu.extend({

        init: function(parent) {
            this._super(parent);
            var switch_button = new instance.web.SwitchOperatingUnitWidget();
            switch_button.appendTo(instance.webclient.$el.find('.oe_systray'));
        }

    });

};
