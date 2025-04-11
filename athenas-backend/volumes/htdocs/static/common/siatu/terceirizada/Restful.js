/**
 *
 **/
Ext._define('common.siatu.terceirizada.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuTerceirizada',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.terceirizada.Restful.superclass.getFields.call(this).concat([
               {name: 'nome', type: 'string'},
               {name: 'cnpj', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'common.siatu.terceirizada.Restful',
    'common.siatu.terceirizada.Grid'
);
