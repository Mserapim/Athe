/**
 *
 **/
Ext._define('adm.patrimonio.entrada.ItemEntradaRestful', {
    extend: 'core.Restful',

    resource: 'PATItemEntrada',

    getFields: function() {
        return adm.patrimonio.entrada.ItemEntradaRestful.superclass.getFields().concat([
            {"name": "meses_garantia", type: 'int'},
            {"name": "nota_unicode", type: 'string'},
            {"name": "especie", type: 'int'},
            {"name": "valor_unitario", type: 'float'},
            {"name": "valor_total", type: 'float'},
            {"name": "quantidade", type: 'int'},
            {"name": "conservacao_display", type: 'string'},
            {"name": "especie_unicode", type: 'string'},
            {"name": "nota", type: 'int'},
            {"name": "unicode", type: 'string'},
            {"name": "conservacao", type: 'int'},
            {"name": "pk", type: 'int'},
            {"name": "icons", type: 'auto'},
            {"name": "descricao", type: 'string'}
        ]);
    }
});
