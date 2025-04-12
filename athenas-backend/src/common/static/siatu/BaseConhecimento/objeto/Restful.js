/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.objeto.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuObjeto',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.BaseConhecimento.objeto.Restful.superclass.getFields.call(this).concat([
               {name: 'descricao', type: 'string'},
               {name: 'informatica', type: 'boolean'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'common.siatu.BaseConhecimento.objeto.Restful',
    'common.siatu.BaseConhecimento.objeto.Grid'
);
