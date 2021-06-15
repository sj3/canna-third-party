odoo.define('operating_unit_isolation.operating_unit_isolation', function (require) {
  "use strict";

  var BasicModel = require('web.BasicModel');

  BasicModel.include({

    _getContext: function(element, options) {
      var v_context = this._super(element, options);

      var extra_context = {
        record: {
          _name: element.model
        },
        parent_record: {}
      };

      if (options) {
        extra_context.record._field = options.fieldName;
      };
      var data = this.get(element.id).data;
      if (data && data.operating_unit_id) {
        extra_context.record.operating_unit_id = data.operating_unit_id.data && data.operating_unit_id.data.id;
      };

      /* FIXME only hardcoded for sale.order.line */
      if (element.model === 'sale.order.line' && 'model' in this.__parentedParent) {
        var parent_data = this.__parentedParent.model.get(this.__parentedParent.handle).data;
        if (parent_data && 'operating_unit_id' in parent_data && parent_data.operating_unit_id) {
          /* FIXME */
          extra_context.parent_record._o2m = 'order_id';
          extra_context.parent_record.operating_unit_id = parent_data.operating_unit_id.data && parent_data.operating_unit_id.data.id;
        }
      }

      /* V8 code
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

      return v_context;
    }
  });

});
