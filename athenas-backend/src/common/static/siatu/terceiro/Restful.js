/**
 *
 **/
Ext._define('common.siatu.terceiro.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuTerceiroInterno',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.terceiro.Restful.superclass.getFields.call(this).concat([
               {name: 'busy', type: 'auto'},
               {name: 'nome', type: 'string'},
               {name: 'cpf', type: 'string'},
               {name: 'telefone', type: 'string'},
               {name: 'endereco', type: 'string'},
            ]);

        return this._fields;
    }
});
