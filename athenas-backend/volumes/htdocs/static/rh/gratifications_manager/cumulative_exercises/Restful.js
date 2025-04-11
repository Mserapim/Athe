 Ext._define('rh.gratifications_manager.cumulative_exercises.Restful', {
    extend: 'core.Restful',

    resource: 'GMCumulativeExercises',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.gratifications_manager.cumulative_exercises.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "servidor", useNull: true},
                {type: "string", name: "servidor_unicode"},
                {type: "string", name: "titularidade"},
                {type: "string", name: "cumulativa"},
                {type: "string", name: "servidor_substituido_unicode"},
                {type: "datetime", name: "data_inicio" },
                {type: "datetime", name: "data_fim" },
                {type: "string", name: "qtd_dias"},
                {type: "string", name: "periodo_pgto"},
                {type: "string", name: "gedoc"},
                {type: "string", name: "payment_installments"},
                {name: "icons", type: 'auto'},
                {type: "boolean", name: "able_to_pay"},
                {type: "boolean", name: "paid_out"},
                {type: "boolean", name: "indeferido"},
                {type: "boolean", name: "retroativo"},
                {type: 'string', name: 'pay_month'},
                {type: 'string', name: 'pay_year'},
                {type: "datetime", name: "data_pgto_inicio" },
                {type: "datetime", name: "data_pgto_fim" },
                {type: 'string', name: 'periodo'},
            ]);

        return this._fields;
    }
});
