/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful', {
    extend: 'core.Restful',

    resource: 'GFPReferenciaNiveis2DRestful',

    remote: false,

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.ReferenciaNiveis2DRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'estrutura_salarial', type: 'int'},
            {name: 'estrutura_salarial_unicode', type: 'string'},
            {name: 'referencia_anterior', type: 'int'},
            {name: 'referencia_anterior_unicode', type: 'string'},
            {name: 'horizontal', type: 'string'},
            {name: 'vertical', type: 'string'},
            {name: 'sigla_cache', type: 'string'},
            {name: 'ordem', type: 'int'},
            {name: 'tipo_valor', type: 'int'},
            {name: 'months_progression', type: 'int'},
            {name: 'tipo_valor_display', type: 'string'},
            {name: 'tipo_gratificacao', type: 'int'},
            {name: 'tipo_gratificacao_display', type: 'string'},
            {name: 'tipo_valor_membro', type: 'int'},
            {name: 'tipo_valor_membro_display', type: 'string'},
            {name: 'tipo_gratificacao_membro', type: 'int'},
            {name: 'tipo_gratificacao_membro_display', type: 'string'},
            {name: 'ativo', type: 'boolean'},
            {name: 'fator_atualizacao', type: 'float'},            
        ]);
    }
});
