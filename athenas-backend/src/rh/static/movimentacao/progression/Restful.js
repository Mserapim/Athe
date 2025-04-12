/**
 *
 **/
Ext._define('rh.movimentacao.progression.Restful', {
    extend: 'rh.movimentacao.pessoal.Restful',

    resource: 'GFPProgression',

    constructor: function(cfg) {
        rh.movimentacao.progression.Restful.superclass.constructor.call(this, cfg);
    },

    getFields: function() {
        if(!this._fields){
            this._fields = rh.movimentacao.progression.Restful.superclass.getFields.call(this, {}).concat([
                {type: "date", name: "data_alteracao", dateFormat: "d/m/Y"}, 
                {type: "date", name: "data_fim_vigencia", dateFormat: "d/m/Y"}, 
                {type: "int", name: "progressao_anterior", useNull: true}, 
                {type: "string", name: "progressao_anterior_unicode"}, 
                {type: "date", name: "data_referencia_inicial", dateFormat: "d/m/Y"}, 
                {type: "date", name: "data_inicio_vigencia", dateFormat: "d/m/Y"}, 
                {type: "date", name: "data_referencia", dateFormat: "d/m/Y"}, 
                {type: "date", name: "data_vigencia", dateFormat: "d/m/Y"}, 
                {type: "date", name: "expected_date", dateFormat: "d/m/Y"}, 
                {type: "date", name: "initial_expected_date", dateFormat: "d/m/Y"}, 
                {type: "int", name: "movimentacao_posse", useNull: true}, 
                {type: "string", name: "movimentacao_posse_unicode"}, 
                {type: "int", name: "referencia_nivel2d", useNull: true}, 
                {type: "string", name: "referencia_nivel2d_unicode"}, 
                {type: "string", name: "dias_suspenso"}, 
                {type: "bool", name: "indireto"}, 
                {type: "string", name: "titulo"}, 
                {type: "bool", name: "ativo"}, 
                {type: "string", name: "dias_suspenso_afastamento"},
                {type: "string", name: "next_reference"},
                {type: "int", name: "extends"},
                {type: "int", name: "period_absences"},
                {type: "int", name: "months_progression"},
                {type: "string", name: "type_progression"},
            ]);
        }
        return this._fields;
    }
});
