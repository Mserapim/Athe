/**
 *
 **/
Ext._define('adm.patrimonio.parametro.SequenciaRestful', {
    extend: 'core.Restful',

    resource: 'PATSequencia',

    getFields: function() {
        var fields = adm.patrimonio.parametro.SequenciaRestful.superclass.getFields.call(this);

        return fields.concat([
            {name: 'titulo', type: 'string'},
            {name: 'proximo', type: 'int'}
        ]);
    }
});
