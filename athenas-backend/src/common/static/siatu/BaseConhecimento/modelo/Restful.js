/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.modelo.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuModelo',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.BaseConhecimento.modelo.Restful.superclass.getFields.call(this).concat([
               {name: 'descricao', type: 'string'},
               {name: 'informatica', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'common.siatu.BaseConhecimento.modelo.Restful',
    'common.siatu.BaseConhecimento.modelo.Grid'
);
