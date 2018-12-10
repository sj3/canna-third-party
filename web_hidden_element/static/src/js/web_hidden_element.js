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

    instance.web.ListView.List.include({
        hidden_cells: {},
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
                if (eval == hidden) {
                    record.attributes[field.name] = false;
                }
                if (!(field.name in this.hidden_cells)) {
                    this.hidden_cells[field.name] = [];
                }
                this.hidden_cells[field.name].push(eval);
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
            for (var field in this.hidden_cells) {
                var hide_column = _.every(
                    this.hidden_cells[field],
                    function(f) {
                        return f;
                    }
                );

                if (hide_column) {
                    // Remove header
                    var th_rule = _.str.sprintf("th[data-id='%s'] {display: none;}", field);
                    if (!$("style").html().includes(th_rule)){
                        $("style").append(_.str.sprintf("th[data-id='%s'] {display: none;}", field));
                    }
                    // Remove cells (including aggregates)
                    var td_rule = _.str.sprintf("td[data-field='%s'] {display: none;}", field);
                    if (!$("style").html().includes(td_rule)){
                        $("style").append(_.str.sprintf("td[data-field='%s'] {display: none;}", field));
                    }
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
