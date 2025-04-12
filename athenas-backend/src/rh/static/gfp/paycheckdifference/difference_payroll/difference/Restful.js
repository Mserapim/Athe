Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.Restful', {
    extend: 'core.Restful',

    resource: 'GFPDifferencePayroll',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gfp.paycheckdifference.difference_payroll.difference.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "period_unicode", type: "string"},
                {name: "employee", type: "int", useNull: true},
                {name: "employee_unicode", type: "string"},
                {name: "event_unicode", type: "string"},
                {name: "payroll_event", type: "string"},
                {name: "qtd_normalize", type: "string"},
                {name: "correct_value_event", type: "float", useNull: true},
                {name: "base_value_event", type: "float", useNull: true},
                {name: "event_info", type: "string"},
                {name: "qtd_diff_normalize", type: "string"},
                {name: "correct_value_diff", type: "float", useNull: true},
                {name: "value_diff", type: "float", useNull: true},
                {name: "diff_info", type: "string"},
                {name: "base_value_diff", type: "float", useNull: true},
                {name: "payroll_applied", type: "string"},
                {name: "event_diff_unicode", type: "string"},
                {name: "icons", type: 'auto'},
                {name: "created_at", type: 'datetime'},
            ]);

        return this._fields;
    }
});
