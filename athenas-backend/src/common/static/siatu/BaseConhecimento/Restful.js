/**
 *
 **/
Ext._define('common.siatu.BaseConhecimento.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuBaseConhecimento',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.BaseConhecimento.Restful.superclass.getFields.call(this).concat([
               {name: 'objeto', type: 'int'},
               {name: 'objeto_string', type: 'string'},
               {name: 'modelo', type: 'int'},
               {name: 'modelo_string', type: 'string'},
               {name: 'problema', type: 'string'},
               {name: 'solucao', type: 'string'},
               {name: 'arquivo', type: 'int'},
               {name: 'filename', type: 'string'},
               {name: 'permalink', type: 'string'},
            ]);

        return this._fields;
    }
});

core.RestfulGrid.register(
    'common.siatu.BaseConhecimento.Restful',
    'common.siatu.BaseConhecimento.Grid'
);
