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
            if (this.operating_units.length === 1) {
                this.$el.hide();
            }
            else{
                this.$el.show();
                this.$el.find('.easy_switch_operating_unit_operating_unit_item').on('click', function(ev) {
                    var operating_unit_id = $(ev.target).data("operating.unit-id");


                    if (operating_unit_id != self.current_operating_unit_id){
                        var func = '/web_easy_switch_operating_unit/switch/change_current_operating_unit';
                        var param = {'operating_unit_id': operating_unit_id}
                        self.rpc(func, param).done(function(res) {
                            window.location.reload()
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
         * - Load data of the operating.units allowed to the current users;
         * - Launch the rendering of the current widget;
         */
        _load_data: function(){
            var self = this;
            // Request for current users information
            this._fetch('res.users',['default_operating_unit_id','operating_unit_ids'],[['id','=',this.session.uid]]).then(function(res_users){
                self.current_operating_unit_id = res_users[0].default_operating_unit_id[0];
                self.current_operating_unit_name = res_users[0].default_operating_unit_id[1];
                // Request for other operating.units

                new instance.web.Model("operating.unit")
                    .query(['id','name'])
                    .all().then(function (data) {
                        _(data).each(function(operating_unit){
                            var logo_state;
                            if (operating_unit.id == self.current_operating_unit_id){
                                logo_state = '/web_easy_switch_operating_unit/static/description/selection-on.png';
                            }
                            else{
                                logo_state = '/web_easy_switch_operating_unit/static/description/selection-off.png';
                            }
                            if (operating_unit.id in  res_users[0].operating_unit_ids) {
                                self.operating_units.push({
                                    id: operating_unit.id,
                                    name: operating_unit.name,
                                    logo_state: logo_state
                                });
                            }
                        });
                    self.renderElement();
                })

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

