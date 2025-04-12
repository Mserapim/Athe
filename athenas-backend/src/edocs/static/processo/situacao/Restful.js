/**
 *
 **/
Ext._define('edocs.processo.situacao.Restful', {
    extend: 'core.Restful',

    resource: 'EpadSituacao',

    getFields: function() {
        if(!this._fields)
            this._fields = edocs.processo.situacao.Restful.superclass.getFields.call(this).concat([
              {name: 'nome', type: 'string'},
            ]);

        return this._fields;
    }
});