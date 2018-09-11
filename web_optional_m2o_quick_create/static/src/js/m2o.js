openerp.web_optional_m2o_quick_create = function(instance) {
  instance.web.form.FieldMany2One.include({
    init: function(field_manager, node) {
      var self = this;
      this._super(field_manager, node);
      model = new instance.web.Model('ir.model');
      if (! _.has(this.options, 'no_create')) {
        this.options.no_create = true;
      }
      if (! _.has(this.options, 'no_quick_create')) {
        this.options.no_quick_create = true;
      }
    }
  });
}