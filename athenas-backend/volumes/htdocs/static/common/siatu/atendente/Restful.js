/**
 *
 **/
Ext._define('common.siatu.atendente.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuAtendente',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.atendente.Restful.superclass.getFields.call(this).concat([
               {name: 'busy', type: 'auto'},
               {name: 'username', type: 'string'},
               {name: 'nome', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'common.siatu.atendente.Restful',
    'common.siatu.atendente.Grid'
);