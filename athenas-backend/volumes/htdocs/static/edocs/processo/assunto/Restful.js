/**
 *
 **/
Ext._define('edocs.processo.assunto.Restful', {
    extend: 'core.Restful',

    resource: 'EpadAssunto',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.assunto.Restful.superclass.getFields.call(this).concat([
              {name: 'nome', type: 'string'},
            ]);

        return this._fields;
    }
});