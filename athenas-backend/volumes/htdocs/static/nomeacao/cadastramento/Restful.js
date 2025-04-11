 Ext._define("nomeacao.cadastramento.Restful", {
    extend: 'core.Restful',

    resource: 'NOMConviteNomeacao',

    getFields: function() {
        if(!this._fields){
            this._fields = nomeacao.cadastramento.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "comarca", useNull: true},
                {type: "string", name: "cpf"},
                {type: "string", name: "nome"},
                {type: "string", name: "nome_social"},
                {type: "bool", name: "sinc_form", useNull: true},
                {type: "datetime", name: "created_at"},
            ]);
        }
        return this._fields;
    }
});