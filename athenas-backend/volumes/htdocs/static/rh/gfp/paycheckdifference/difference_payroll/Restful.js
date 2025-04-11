 Ext._define('rh.gfp.paycheckdifference.difference_payroll.Restful', {
    extend: 'core.Restful',

    resource: 'GFPPeriodPayroll',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.paycheckdifference.difference_payroll.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'month', type: 'string'},
                {name: 'year', type: 'int'},
                {name: 'period', type: 'string'},
                {name: 'qtd_diff', type: 'int'},
                {name: 'qtd_diff_applied', type: 'int'},
                {name: 'qtd_diff_ignored', type: 'int'},
                {name: 'calculate_last_date', type: 'datetime'},
            ]);

        return this._fields;
    }
});
