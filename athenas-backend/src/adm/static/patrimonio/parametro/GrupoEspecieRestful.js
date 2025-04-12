/**
 *
 **/
Ext._define('adm.patrimonio.parametro.GrupoEspecieRestful', {
    extend: 'core.Restful',

    resource: 'PATGrupoEspecie',

    getFields: function() {
        var fields = adm.patrimonio.parametro.GrupoEspecieRestful.superclass.getFields.call(this);

        return fields.concat([
            {name: 'titulo', type: 'string'},
            {name: 'codigo', type: 'int'}
        ]);
    }
});
