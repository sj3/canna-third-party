window.hidden_cells = {};

openerp.web_hidden_element = function(instance) {
    instance.web.form.FormWidget.include({
        process_modifiers: function() {
            var res = this._super.apply(this, arguments);
            if (this.node.attrs.invisible_expression) {
                var expression = py.parse(py.tokenize(this.node.attrs.invisible_expression));
                var eval = py.evaluate(expression, this.field_manager.build_eval_context().eval()).toJSON();
                var invisible = eval == py.eval(this.node.attrs.hidden);
                // To implement "override modifiers", change the condition:
                if (invisible){
                    this.set({
                        invisible: invisible
                    });
                    try {
                        if (this.el.parentNode.parentNode.nodeName == "TR") {
                            this.el.parentNode.parentNode.remove();
                        }
                    }
                    catch (error){ }
                }
            }
            return res;
        }
    });

    instance.web.ViewManager.include({
    /**
     * @override
     */
        switch_mode: function(view_type, no_store, view_options) {
            // Clear column and cell style hiding rules
            // Note that this does not influence the values of the cells.
            for (var field in window.hidden_cells) {
                var th_rule = _.str.sprintf("th[data-id='%s'] {display: none;}", field);
                var td_rule = _.str.sprintf("td[data-field='%s'] {display: none;}", field);
                [th_rule, td_rule].forEach(function(rule) {
                    $("style").each(function(i) {
                        if (this.innerHTML.includes(rule)) {
                            this.innerHTML = this.innerHTML.replace(rule, '');
                        }
                    });
                });
            }
            // Clear hidden_cells so they don't influence the newly opened view
            window.hidden_cells = {};
            var res = this._super.apply(this, arguments);
            return res;
        }
    });

    instance.web.ListView.List.include({
        /**
         * @override
         */
        render_cell: function(record, field) {
            if (field.invisible_expression) {
                var ctx = record.toContext();
                var parent_ctx = this.dataset.get_context().__eval_context;
                if (parent_ctx)
                    ctx.parent = parent_ctx.__contexts[1];
                var expression = py.parse(py.tokenize(field.invisible_expression));
                var eval = py.evaluate(expression, ctx).toJSON();
                var hidden = py.eval(field.hidden);

                if (hidden && eval) {
                    // Hide the values
                    record.attributes[field.name] = false;
                }
                if (!(field.name in window.hidden_cells)) {
                    window.hidden_cells[field.name] = [];
                }
                // hidden_cells will be used to remove columns and cells in
                // list views.
                if (!window.hidden_cells[field.name].includes(eval)){
                    window.hidden_cells[field.name].push(eval);
                }
            }
            var res = this._super.apply(this, arguments);
            return res;
        },

        /**
         * Hides all columns that need to be hidden.
         *
         * @private
         */
        hide_empty_columns: function() {
            for (var field in window.hidden_cells) {
                if ($('style').length == 0) {
                    $('head').append("<style></style>");
                }
                if (window.hidden_cells[field].length > 0) {
                    var hide_column = !window.hidden_cells[field].includes(false);
                }
                else {
                    var hide_column = false;
                }
                if (hide_column) {
                    // Add "Hide header" and "Hide cell" rules
                    var th_rule = _.str.sprintf("th[data-id='%s'] {display: none;}", field);
                    var td_rule = _.str.sprintf("td[data-field='%s'] {display: none;}", field);
                    [th_rule, td_rule].forEach(function(rule) {
                        $("style:first").each(function(i) {
                            if (!this.innerHTML.includes(rule)) {
                                this.innerHTML += rule;
                            }
                        });
                    });
                }
            }
        },

        /**
         * @override
         */
        render: function() {
            var res = this._super.apply(this, arguments);
            this.hide_empty_columns();
            return res;
        }
    });
};
