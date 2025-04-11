 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.periodo.Restful', {
    extend: 'core.Restful',

    resource: 'GMPeriodoExercCumulPermanente',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_permanent.periodo.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'ano', type: 'int'},
                {name: 'mes', type: 'string'},
                {name: 'periodo', type: 'string'},
                {name: 'data_ultimo_calculo', type: 'datetime'},
            ]);

        return this._fields;
    }
});
