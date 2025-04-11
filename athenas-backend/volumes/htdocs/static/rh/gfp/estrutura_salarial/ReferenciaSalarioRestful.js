/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.ReferenciaSalarioRestful', {
    extend: 'core.Restful',

    resource: 'GFPReferenciaSalarioRestful',

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.ReferenciaSalarioRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'tabela_salarial', type: 'int'},
            {name: 'tabela_salarial_unicode', type: 'string'},
            {name: 'referencia_nivel2d', type: 'int'},
            {name: 'referencia_nivel2d_unicode', type: 'string'},
            {name: 'valor', type: 'float'},
            {name: 'gratificacao', type: 'float'},
            {name: 'valor_membro', type: 'float'},
            {name: 'gratificacao_membro', type: 'float'},
            {name: 'sigla_cache', type: 'string'},
        ]);
    }
});
