 Ext._define('rh.gratifications_manager.member_gratifications.gratificacoes.Restful', {
    extend: 'core.Restful',

    resource: 'GMGratificacoes',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.member_gratifications.gratificacoes.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons", type: "auto"},
                {name: 'evento_unicode', type: 'string'},
                {name: 'servidor_unicode', type: 'string'},
                {name: 'qtd_dias_consolidado', type: 'int'},
                {name: 'qtd_dias_deferido', type: 'string'},
                {name: 'status', type: 'string'},
                {name: 'data_ultimo_calculo', type: 'datetime'},
                {name: 'cumulativa', type: 'bool'},
                {name: 'principal', type: 'bool'},
                {name: 'grat_membro_id', type: 'int'},
            ]);

        return this._fields;
    }
});