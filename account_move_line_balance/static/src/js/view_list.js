openerp.account_move_line_balance = function(instance) {
    instance.web.list.Column.include({
        /*
         * @override
         * Search for the additional balance attribute and return the
         * function which returns which columns have aggregates.
         */
        to_aggregate: function () {
            this._super.apply(this, arguments);
            if (this.type !== 'integer' && this.type !== 'float') {
                return {};
            }

            var aggregation_func = (this.sum && 'sum') || (this.avg && 'avg') ||
                (this.max && 'max') || (this.min && 'min') ||
                (this.balance && 'balance');

            if (!aggregation_func) {
                return {};
            }

            var C = function (fn, label) {
                this['function'] = fn;
                this.label = label;
            };
            C.prototype = this;
            return new C(aggregation_func, this[aggregation_func]);
        },
    }),
    instance.web.ListView.include({
        /*
         * @override
         * Compute the additional balance aggregate by subtracting credit from
         * debit.
         */
        compute_aggregates: function (records) {
            this._super.apply(this, arguments);
            var columns = _(this.aggregate_columns).filter(function (column) {
                return column['function']; });
            if (_.isEmpty(columns)) { return; }

            if (_.isEmpty(records)) {
                records = this.groups.get_records();
            }
            records = _(records).compact();

            var count = 0, sums = {};
            _(columns).each(function (column) {
                switch (column['function']) {
                    case 'max':
                        sums[column.id] = -Infinity;
                        break;
                    case 'min':
                        sums[column.id] = Infinity;
                        break;
                    default:
                        sums[column.id] = 0;
                }
            });
            _(records).each(function (record) {
                count += record.count || 1;
                _(columns).each(function (column) {
                    var field = column.id,
                    value = record.values[field];
                    switch (column['function']) {
                        case 'sum':
                            sums[field] += value;
                            break;
                        case 'avg':
                            sums[field] += record.count * value;
                            break;
                        case 'min':
                            if (sums[field] > value) {
                                sums[field] = value;
                            }
                            break;
                        case 'max':
                            if (sums[field] < value) {
                                sums[field] = value;
                            }
                            break;
                        case 'balance':
                            // Note that we expect the columns to be called
                            // debit and credit. If they are named differently
                            // this will silently fail.
                            sums[field] = sums['debit'] - sums['credit'];
                            break;
                    }
                });
            });

            var aggregates = {};
            _(columns).each(function (column) {
                var field = column.id;
                switch (column['function']) {
                    case 'avg':
                        aggregates[field] = {value: sums[field] / count};
                        break;
                    default:
                        aggregates[field] = {value: sums[field]};
                }
            });

            this.display_aggregates(aggregates);
        },
    });
}
