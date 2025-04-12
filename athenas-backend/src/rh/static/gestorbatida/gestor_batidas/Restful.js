Ext._define('rh.gestorbatida.gestor_batidas.Restful', {
    extend: 'core.Restful',

    resource: 'RHGestorBatidas',

    response: false,

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gestorbatida.gestor_batidas.Restful.superclass.getFields.call(this, cfg).concat([
                { name: "date_time", type: "string" },
                { name: "employee_name", type: "string" },
                { name: "employee_register", type: "string" },
                { name: "employee_matricula", type: "string" },
                { name: "workplace", type: "string" },
                { name: "ip", type: "string" },
                { name: "marcacao", type: "string" },
                { name: "marcacao_valida", type: "boolean" },
                { name: "tipo_justificativa", type: "string" },
                { name: "tipo_justificativa_label", type: "string" },
                { name: "justificativa", type: "string" },
                { name: "tabela_import", type: "string" },
                { name: "codigo_import", type: "string" },
                { name: "id", type: "int" },
            ]);

        return this._fields;
    },

});
