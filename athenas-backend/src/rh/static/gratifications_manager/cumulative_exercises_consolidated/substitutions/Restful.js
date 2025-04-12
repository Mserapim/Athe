 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Restful', {
    extend: 'core.Restful',

    resource: 'GMCumulativeExercisesConsolidatedSubstitutions',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "servidor", useNull: true},
                {type: "string", name: "servidor_unicode"},
                {type: "string", name: "titularidade"},
                {type: "string", name: "cumulativa"},
                {type: "string", name: "servidor_substituido_unicode"},
                {type: "string", name: "qtd_dias"},
                {type: "datetime", name: "data_inicio" },
                {type: "datetime", name: "data_fim" },
            ]);

        return this._fields;
    }
});
