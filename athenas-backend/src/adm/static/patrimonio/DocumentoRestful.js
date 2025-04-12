/**
 *
 **/
Ext._define('adm.patrimonio.DocumentoRestful', {
    extend: 'core.Restful',

    resource: 'PATDocumento',

    getFields: function() {
        return adm.patrimonio.DocumentoRestful.superclass.getFields().concat([
            {"name": "icons", type: 'auto'},
            {"name": "mimetype", type: 'string'},
            {"name": "titulo", type: 'string'},
            {"name": "criado", type: 'date', dateFormat: 'd/m/Y H:i'},
            {"name": "criado_por", type: 'string'},
            {"name": "permalink", type: 'string'},
            {"name": "data", type: 'int'},
        ]);
    }
});
