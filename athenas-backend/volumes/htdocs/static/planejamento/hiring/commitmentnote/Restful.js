
Ext._define('planning.hiring.commitmentnote.Restful', {
    extend: 'core.Restful',

    resource: 'PHACommitmentNote',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.commitmentnote.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "icons"
                },
                {
                    type: "string",
                    name: "numero_ne"
                },
                {
                    type: "int",
                    name: "ne_anterior",
                    useNull: true
                },
                {
                    type: "string",
                    name: "saldo"
                },
                {
                    type: "string",
                    name: "principal"
                },
                {
                    type: "float",
                    name: "valor"
                },
                {
                    type: "int",
                    name: "tipo"
                },
                {
                    type: "string",
                    name: "tipo_ne_display"
                },
                {
                    type: "int",
                    name: "classificacao"
                },
                {
                    type: "int",
                    name: "fornecedor"
                },
                {
                    type: "string",
                    name: "fornecedor_display"
                },
                {
                    type: "int",
                    name: "ref_valor_contrato"
                },
                {
                    type: "int",
                    name: "prazo_entrega"
                },
            ]);

        return this._fields;
    }
});
