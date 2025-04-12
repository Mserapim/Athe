Ext._define("rh.nomeacao.Restful", {
    extend: 'core.Restful',

    resource: 'RHNomeacaoRestful',

    getFields: function() {
        if(!this._fields){
            this._fields = rh.nomeacao.Restful.superclass.getFields.call(this, {}).concat([
                {type: "string", name: "tipo_nomeacao"},
                {type: "int", name: "provimento"},
                {type: "string", name: "provimento_unicode"},
                {type: "string", name: "cpf"},
                {type: "date", name: "data_convocacao", dateFormat: "d/m/Y"},
                {type: "date", name: "data_resposta", dateFormat: "d/m/Y"},
            ]);
        }
        return this._fields;
    }
});