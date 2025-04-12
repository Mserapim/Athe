/**
 *
 **/
Ext._define('common.siatu.gerente.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuGerente',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.gerente.Restful.superclass.getFields.call(this).concat([
               {name: 'username', type: 'string'},
               {name: 'nome', type: 'string'},
            ]);

        return this._fields;
    }
});
