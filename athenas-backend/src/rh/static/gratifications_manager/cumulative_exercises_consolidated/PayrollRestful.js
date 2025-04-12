Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.PayrollRestful', {
    extend: 'core.Restful',

    resource: 'GMCumulativeExercisesConsolidatedPayroll',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_consolidated.PayrollRestful.superclass.getFields.call(this, cfg).concat([
                {type: 'int',name: 'id'},
                {type: 'bool', name: 'processado'},
                {type: 'int', name: 'periodo', useNull: true},
                {type: 'string', name: 'periodo_unicode'},
                {type: 'string', name: 'processado_por_unicode'},
                {type: 'int', name: 'status', useNull: true},
                {type: 'string', name: 'status_display'},
                {type: 'string', name: 'fechado_por_unicode'},
                {type: 'int', name: 'tipo_folha', useNull: true},
                {type: 'string', name: 'tipo_folha_unicode'},
                {name: 'icons'},
                {type: 'int', name: 'periodo_ano'},
                {type: 'int', name: 'periodo_mes'},
                {type: 'bool', name: 'is_working'},
                {type: 'string', name: 'complement'},
                {type: 'string', name: 'complement_display'},
                
            ]);

        return this._fields;
    }
});


Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.OpendedPayrollRestful', {
    extend: 'rh.gratifications_manager.cumulative_exercises_consolidated.PayrollRestful',

    resource: 'GFPOpenedPayroll',

});
