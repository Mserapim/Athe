/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.TabelaSalarialRestful', {
    extend: 'core.Restful',

    resource: 'GFPTabelaSalarialRestful',

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.TabelaSalarialRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'estrutura_salarial', type: 'int'},
            {name: 'estrutura_salarial_unicode', type: 'string'},
            {name: 'tabela_anterior', type: 'int', useNull: true},
            {name: 'tabela_anterior_unicode', type: 'string'},
            {name: 'info_adicional', type: 'string'},
            {name: 'start_validity', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'end_validity', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'publicacao', type: 'int', useNull: true},
            {name: 'publicacao_unicode', type: 'string'},
            {name: 'identifier', type: 'int'},
            {name: 'identifier_display', type: 'string'}
        ]);
    }
});
