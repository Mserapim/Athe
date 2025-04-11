/**
 *
 **/
Ext._define('rh.movimentacao.substituicao.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'RHMovimentacaoSubstituicaoRestful',

    constructor: function(cfg) {
        rh.movimentacao.substituicao.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.movimentacao.substituicao.Restful.superclass.getFields.call(this, {}).concat([
                {type: "int", name: "publicacao_fim", useNull: true},
                {type: "string", name: "publicacao_fim_unicode"},
                {type: "date", name: "data_fim", dateFormat: "d/m/Y"},
                {type: "int", name: "servidor_substituido", useNull: true},
                {type: "string", name: "servidor_substituido_unicode"},
                {type: "int", name: "afastamento", useNull: true},
                {type: "string", name: "afastamento_unicode"},
                {type: "int", name: "posse", useNull: true},
                {type: "string", name: "posse_unicode"},
                {type: "date", name: "data_prevista", dateFormat: "d/m/Y"},
                {type: "date", name: "data_inicio", dateFormat: "d/m/Y"},
                {type: "string", name: "posse_cargo_unicode"},
                {type: "string", name: "departure_reason_unicode"},
                {type: "string", name: "situation_unicode"},
                {type: "auto", name: "icons"},
                // {type: "boolean", name: "automatic_substitute"},
                {type: "int", name: "designation_substitute", useNull: true},
                {type: "string", name: "designation_substitute_unicode"},
                {type: "int", name: "designation_substituted", useNull: true},
                {type: "string", name: "designation_substituted_unicode"},
                {type: "boolean", name: "ordinance"},
                {type: 'string', name: 'pay_month'},
                {type: 'string', name: 'pay_year'},
                {type: "string", name: "gedoc", useNull: true},
                {type: "int", name: "payment_installments", useNull: true},
                {type: "boolean", name: "able_to_pay"},
                {type: "boolean", name: "consolidated"},
                {type: "boolean", name: "paid_out"},
                { type: "int", name: "origin_register", useNull: true },
                { type: "string", name: "origin_register_display" },
                {type: "boolean", name: "retroativo"},

            ]);
        }
        return this._fields;
    }
});
