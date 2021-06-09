odoo.define('operating_unit_isolation.operating_unit_isolation', function (require) {

  var BasicModel = require('web.BasicModel');

  BasicModel.include({

    _getContext: function(element, options) {
      var v_context = this._super(element, options);
      /*
      console.log("operating_unit_isolation, _getContext");
      console.log('this=',this);
      console.log('element=', element);
      console.log('options=', options);
      */
      var extra_context = {
        record: {
          _name: element.model,
        },
        parent_record: {}
      };

      if (options) {
        extra_context.record._field = options.fieldName;
      };
      var data = this.get(element.id).data;
      console.log('data=', data); //DEBUG
      if (data && data.operating_unit_id) {
        extra_context['record']['operating_unit_id'] = data.operating_unit_id.data && data.operating_unit_id.data.id;
      };
      var parent = this.__parentedParent; //DEBUG
      console.log('parent=', parent); //DEBUG
      /*      
      if (this.field_manager.dataset && this.field_manager.dataset.parent_view) {
        extra_context['parent_record']['_name'] = this.field_manager.dataset.parent_view.model;
        if (this.field_manager.dataset.o2m && this.field_manager.dataset.o2m.field.relation_field) {
          extra_context['parent_record']['_o2m'] = this.field_manager.dataset.o2m.field.relation_field;
        }
        $.each(this.field_manager.dataset.parent_view.fields, function (key, value) {
          extra_context['parent_record'][key] = value.get_value();
        });
      }
       */
      _.extend(v_context, extra_context);
      console.log(v_context);

      return v_context;
    }
  });

});
