openerp.web_disable_export_group = function(instance) {

    var _t = instance.web._t;
    var SUPERUSER_ID = 1;

    instance.web.Sidebar.include({
        add_items: function(section_code, items) {
            var self = this;
            var _super = this._super;
            if (this.session.uid == SUPERUSER_ID) {
                _super.apply(this, arguments);
            } else {
                var model_res_users = new openerp.web.Model("res.users");
                model_res_users.call("may_export", [self.view.dataset.model]).done(function(can_export) {
                    if (!can_export) {
                        var export_label = _t("Export");
                        var new_items = items;
                        if (section_code === "other") {
                            new_items = [];
                            for (var i = 0; i < items.length; i++) {
                                if (items[i]["label"] !== export_label) {
                                    new_items.push(items[i]);
                                }
                            }
                        }
                        if (new_items.length > 0) {
                            _super.call(self, section_code, new_items);
                        }
                    } else {
                        _super.call(self, section_code, items);
                    }
                });
            }
        }
    });
};
