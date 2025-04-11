 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Restful', {
    extend: 'core.Restful',

    resource: 'GMExercCumulPermanenteDesignacoes',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons", type: "auto"},
                {name: 'servidor', type: 'string'},
                {name: 'designacao_unicode', type: 'string'},
                {name: 'substituicao', type: 'bool'},
                {name: 'base_calculo', type: 'bool'},
                {name: 'pct', type: 'string'},
                {name: 'data_vigencia_inicio', type: 'datetime'},
                {name: 'data_vigencia_fim', type: 'datetime'},
            ]);

        return this._fields;
    }
});
