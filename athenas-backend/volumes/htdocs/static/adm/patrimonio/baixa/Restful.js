/**
 *
 **/
Ext._define('adm.patrimonio.baixa.Restful', {
    extend: 'core.Restful',

    resource: 'PATNotaBaixa',

    getFields: function() {
        return adm.patrimonio.baixa.Restful.superclass.getFields.call(this).concat([
            {name: 'icons', type: 'auto'},
            {name: 'conta_unicode', type: 'string'},
            {name: 'conta', type: 'int'},
            {name: 'pre_baixa_unicode', type: 'string'},
            {name: 'numero', type: 'int'},
            {name: 'cache_numero', type: 'string'},
            {name: 'pre_baixa', type: 'int'},
            {name: 'pre_baixa_unicode', type: 'string'},
            {name: 'state_display', type: 'string'},
            {name: 'state', type: 'int'},
            {name: 'processo', type: 'string'},
            {name: 'documento', type: 'string'},
            {name: 'data_documento', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'liquidacao', type: 'string'},
            {name: 'data_liquidacao', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'data_baixa', type: 'date', dateFormat: 'd/m/Y'},
            {name: 'type', type: 'string'}
        ]);
    }
});
