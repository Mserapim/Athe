Ext._define('rh.lista_antiguidade_membros.Restful', {
    extend: 'core.Restful',

    resource: 'ListaAntiguidadeRestfull',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.lista_antiguidade_membros.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "ordem_antiguidade", useNull: true},
                {type: "string", name: "matricula"},
                {type: "string", name: "nome"},
                {type: "string", name: "tipo_cargo"},
                {type: "date", name: "data_inicio_carreira", dateFormat: "d/m/Y"},
                {type: "date", name: "data_inicio_instancia", dateFormat: "d/m/Y"},
                {type: "string", name: "tempo_afastamento_formatado"},
                {type: "string", name: "total_instancia_formatado"},
                {type: "string", name: "efetivo_exercicio_formatado"},
                {type: "string", name: "total_carreira_formatado"},
                {type: "int", name: "posicao_concurso"},
                {type: "datetime", name: "modified_at"},
                {type: "string", name: "modified_by_unicode"},
                {type: "string", name: "origem"}
            ]);

        return this._fields;
    }
});
