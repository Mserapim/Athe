
Ext._define("rh.teletrabalho.teletrabalho_competencia.Restful", {
    extend: 'core.Restful',

    resource: 'TeletrabalhoCompetenciaRestful',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.teletrabalho.teletrabalho_competencia.Restful.superclass.getFields.call(this, {}).concat([
                {type: "date", name: "data_inicio", dateFormat: "d/m/Y"},
                {type: "date", name: "data_fim", dateFormat: "d/m/Y"},
                {type: "string", name: "lotacao", useNull: true},
                {type: "string", name: "matricula", useNull: true},
                {type: "string", name: "email", useNull: true},
                {type: "string", name: "categoria_funcional", useNull: true},
                {type: "string", name: "aprovador"},
                {type: "string", name: "servidor", useNull: true},
                {type: "string", name: "status"},
                {type: "string", name: "ato"},
                {type: "string", name: "gedoc"},
                {type: "string", name: "solicitacao"},
                {type: "string", name: "periodo_ano"},
                {type: "string", name: "periodo_mes"},
            ]);
        }
        return this._fields;
    }
});
