openerp.web_optional_m2o_quick_create = function(instance) {
  instance.web.form.FieldMany2One.include({
    init: function(field_manager, node) {
      var self = this;
      this._super(field_manager, node);
      if (! _.has(this.options, 'no_create')) {
        this.options.no_create = true;
      }
      if (! _.has(this.options, 'no_quick_create')) {
        this.options.no_quick_create = true;
      }
    }
  });

  instance.web.form.FieldMany2ManyTags.include({
    init: function() {
      var self = this;
      this._super.apply(this, arguments);
      if (! _.has(this.options, 'no_create')) {
        this.options.no_create = true;
      }
      if (! _.has(this.options, 'no_quick_create')) {
        this.options.no_quick_create = true;
      }
    }
  });
}