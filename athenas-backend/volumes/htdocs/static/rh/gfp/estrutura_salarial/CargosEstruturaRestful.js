/**
 *
 **/
Ext._define('rh.gfp.estrutura_salarial.CargosEstruturaRestful', {
    extend: 'core.Restful',

    resource: 'GFPCargosEstruturaRestful',

    getFields: function() {
        var fields = rh.gfp.estrutura_salarial.CargosEstruturaRestful.superclass.getFields.call(this);
        return fields.concat([
            {name: 'estrutura_salarial', type: 'int'},
            {name: 'estrutura_salarial_unicode', type: 'string'},
            {name: 'cargo', type: 'int', useNull: true},
            {name: 'cargo_unicode', type: 'string'},
            {name: 'data_vigencia_inicio', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_vigencia_fim', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'publicacao', type: 'int', useNull: true},
            {name: 'publicacao_unicode', type: 'string'},
        ]);
    }
});
