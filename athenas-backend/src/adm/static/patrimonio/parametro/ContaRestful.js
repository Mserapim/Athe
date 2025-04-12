/**
 *
 **/
Ext._define('adm.patrimonio.parametro.ContaRestful', {
    extend: 'core.Restful',

    resource: 'PATConta',

    getFields: function() {
        var fields = adm.patrimonio.parametro.ContaRestful.superclass.getFields.call(this);

        return fields.concat([
            {name: 'titulo', type: 'string'},
            {name: 'principal', type: 'boolean'},
            {name: 'tipo_display', type: 'string'},
            {name: 'prefix', type: 'string'},
            {name: 'sufix', type: 'string'},
            {name: 'tipo', type: 'int'},
            {name: 'sequencia_unicode', type: 'string'},
            {name: 'sequencia', type: 'int'}
        ]);
    }
});
