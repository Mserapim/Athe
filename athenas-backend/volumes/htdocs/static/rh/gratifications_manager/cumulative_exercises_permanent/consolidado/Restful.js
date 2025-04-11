 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Restful', {
    extend: 'core.Restful',

    resource: 'GMExercCumulPermanenteConsolidado',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons", type: "auto"},
                {name: 'servidor_unicode', type: 'string'},
                {name: 'qtd_dias_afastamento', type: 'int'},
                {name: 'qtd_dias_consolidado', type: 'int'},
                {name: 'qtd_dias_deferido', type: 'string'},
                {name: 'pct_consolidado', type: 'string'},
                {name: 'pct_deferido', type: 'string'},
                {name: 'status', type: 'string'},
            ]);

        return this._fields;
    }
});
