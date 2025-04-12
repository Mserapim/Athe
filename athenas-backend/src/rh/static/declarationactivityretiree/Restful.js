/**
 *
 **/
Ext._define('rh.declarationactivityretiree.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'RHDeclarationActivityRetireeRestful',

    constructor: function(cfg) {
        rh.declarationactivityretiree.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.declarationactivityretiree.Restful.superclass.getFields.call(this, {}).concat([
                {type: "date", name: "data_inicio", dateFormat: "d/m/Y"},
                {type: "date", name: "data_encerramento", dateFormat: "d/m/Y"},
                {type: "int", name: "lotacao", useNull: true},
                {type: "string", name: "lotacao_unicode"},
                {type: "bool", name: "ativo"},
                {type: "int", name: "rule"},
                {type: "string", name: "rule_display"},
            ]);
        }
        return this._fields;
    }
});
