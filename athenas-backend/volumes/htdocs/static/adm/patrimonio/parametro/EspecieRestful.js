/**
 *
 **/
Ext._define('adm.patrimonio.parametro.EspecieRestful', {
    extend: 'core.Restful',

    resource: 'PATEspecie',

    getFields: function() {
        var fields = adm.patrimonio.parametro.EspecieRestful.superclass.getFields.call(this);

        return fields.concat([
            {"name": "icons", type: 'auto'},
            {name: 'titulo', type: 'string'},
            {name: 'codigo', type: 'int'},
            {name: 'codigo_cache', type: 'string'},
            {name: 'status', type: 'int'},
        ]);
    }
});
