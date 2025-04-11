 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.Restful', {
    extend: 'core.Restful',

    resource: 'GMCumulativeExercisesConsolidated',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_consolidated.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "employee", useNull: true},
                {type: "string", name: "employee_unicode"},
                {type: "string", name: "titularidade"},
                {type: "string", name: "days_consolidated"},
                {type: "float", name: "value_calculated"},
                {type: "string", name: "periodo_pgto"},
                {type: "string", name: "payroll_applied"},
                {name: "icons", type: 'auto'},
            ]);

        return this._fields;
    }
});
