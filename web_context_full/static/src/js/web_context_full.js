openerp.web_context_full = function (instance) {

  instance.web.form.FormWidget.include({

    build_context: function() {
      var v_context = this._super();
      var extra_context = {
        record: {
          _name: this.field_manager.model,
          _field: this.name
        },
        parent_record: {}
      };

      if (this.field_manager.fields) {
        $.each(this.field_manager.fields, function (key, value) {
          extra_context['record'][key] = value.get_value();
        });
      }
      if (this.field_manager.dataset && this.field_manager.dataset.parent_view) {
        extra_context['parent_record']['_name'] = this.field_manager.dataset.parent_view.model;
        if (this.field_manager.dataset.o2m && this.field_manager.dataset.o2m.field.relation_field) {
          extra_context['parent_record']['_o2m'] = this.field_manager.dataset.o2m.field.relation_field;
        }
        $.each(this.field_manager.dataset.parent_view.fields, function (key, value) {
          extra_context['parent_record'][key] = value.get_value();
        });
      }
      v_context.add(extra_context);

      return v_context;
    }
  });

}