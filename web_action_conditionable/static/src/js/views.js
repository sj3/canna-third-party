/*global openerp, _, $ */

openerp.web_action_conditionable = function (instance) {
    instance.web.View.include({
        /**
         * @override
         */
        is_action_enabled: function(action) {
            var attrs = this.fields_view.arch.attrs;
            if (action in attrs) {
                try {
                    return this._super(action);
                } catch(error) {
                    var expr = attrs[action];
                    var expression = py.parse(py.tokenize(expr));
                    var cxt = this.dataset.get_context().__eval_context;
                    cxt = cxt ? cxt.__contexts[1] : {};
                    cxt['_group_ids'] = instance.session.group_ids;

                    return py.evaluate(expression, cxt).toJSON();
                }
            } else {
                return true;
            }
        },

        /**
         * Checks recursively if an expression uses a field.
         *
         * @private
         * @returns {Boolean}
         */
        _expression_uses_field: function(expression, field) {
            var contains = false;
            if ('expressions' in  expression) {
                contains = _.filter(expression.expressions, function(item) {
                    return item.value === field;
               }).length > 0;
            } else {
                _.each(expression, function(value, key) {
                    if (this._expression_uses_field(value, field)) {
                        contains = true;
                    }
                }.bind(this));
            }
            return contains;
        }
    });
}
