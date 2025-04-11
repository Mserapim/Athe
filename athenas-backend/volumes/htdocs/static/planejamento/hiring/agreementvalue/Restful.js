Ext._define('planning.hiring.agreementvalue.Restful', {
    extend: 'core.Restful',

    resource: 'PHAAgreementValue',

    getFields: function(cfg) {
        if (!this._fields)
            this._fields = planning.hiring.agreementvalue.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "contrato"
                },
                {
                    type: "string",
                    name: "objeto"
                },
                {
                    type: "bool",
                    name: "schedule_annotation"
                },
                {
                    type: "string",
                    name: "data_assinatura"
                },
                {
                    type: "string",
                    name: "data_ref_inicio"
                },
                {
                    type: "string",
                    name: "data_ref_fim"
                },
                {
                    type: "float",
                    name: "valor"
                },
                {
                    type: "string",
                    name: "valor_display"
                },
                {
                    type: "string",
                    name: "data_publicacao"
                },
                {
                    type: "int",
                    name: "ordem"
                },
                {
                    type: "string",
                    name: "ordem_display"
                },
                {
                    type: "int",
                    name: "tipo_valor_contrato"
                },
                {
                    type: "string",
                    name: "tipo_valor_contrato_display"
                },
            ]);

        return this._fields;
    }
});
