/**
 *
 **/
Ext._define('common.siatu.chamado.ItemBaseConhecimento.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuItemBaseConhecimento',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.BaseConhecimento.Restful.superclass.getFields.call(this).concat([
               {name: 'base_conhecimento', type: 'int'},
               {name: 'objeto', type: 'int'},
               {name: 'objeto_string', type: 'string'},
               {name: 'modelo_string', type: 'string'},
               {name: 'problema', type: 'string'},
               {name: 'solucao', type: 'string'},
               {name: 'info', type: 'string'},
            ]);

        return this._fields;
    }
});