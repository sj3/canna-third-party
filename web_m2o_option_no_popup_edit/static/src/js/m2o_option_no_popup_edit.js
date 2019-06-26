openerp.web_m2o_option_no_popup_edit = function (instance) {

    instance.web.form.FieldMany2One.include({

        build_context: function () {
            var v_context = this._super.apply(this, arguments);
            if (!_.has(this.options, 'no_popup_edit') || this.options.no_popup_edit) {
                v_context.add("{'no_popup_edit': 1}");
            }
            return v_context;
        }

    });

    instance.web.form.FormOpenPopup.include({

        show_element: function (model, row_id, context, options) {
            var ctx = context.hasOwnProperty('eval') ? context.eval() : context;
            if (_.has(ctx, 'no_popup_edit') && ctx.no_popup_edit) {
                options.readonly = true;
            };
            return this._super.apply(this, arguments);
        }

    });

}