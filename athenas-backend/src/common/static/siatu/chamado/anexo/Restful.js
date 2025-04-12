/**
 *
 **/
Ext._define('common.siatu.chamado.anexo.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuAnexo',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.chamado.anexo.Restful.superclass.getFields.call(this).concat([
               {name: 'chamado', type: 'int'},
               {name: 'arquivo', type: 'int'},
               {name: 'usuario', type: 'string'},
               {name: 'filename', type: 'string'},
               {name: 'permalink', type: 'string'},
            ]);

        return this._fields;
    }
});
