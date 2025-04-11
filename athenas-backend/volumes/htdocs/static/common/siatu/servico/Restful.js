/**
 *
 **/
Ext._define('common.siatu.servico.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuServico',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.servico.Restful.superclass.getFields.call().concat([
               {name: 'nome', type: 'string'},
               {name: 'servico_superior', type: 'int'},
            ]);

        return this._fields;
    }
});
