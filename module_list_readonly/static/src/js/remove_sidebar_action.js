/*
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/

openerp.module_list_readonly = function(instance) {
    var _t = instance.web._t;

    instance.web.Sidebar.include({

        /* section: keep only 'Export' */
        add_items: function(section_code, items) {
            var ctx = this.getParent().dataset.context;
            // console.log("add_items, ctx=", ctx);
            var ro = ctx['module_list_readonly']
            if (ro == 1) {
                var export_label = _t("Export");
                var new_items = [];
                if (section_code == 'other') {
                    for (var i = 0; i < items.length; i++) {
                        // console.log("items[i]: ", items[i]);
                        if (items[i]['label'] == export_label) {
                            new_items.push(items[i]);
                        };
                    };
                };
                if (new_items.length > 0) {
                    this._super.call(this, section_code, new_items);
                };
            } else {
                this._super.apply(this, arguments);
            };

        },

    });

};
