/**
 *
 **/
Ext._define('common.siatu.chamado.status.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuStatus',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.chamado.status.Restful.superclass.getFields.call(this).concat([
               {name: 'status', type: 'int'},
               {name: 'icon', type: 'auto'},
               {name: 'status_display', type: 'string'},
               {name: 'data_inicio', type: 'string'},
               {name: 'previsao_fim', type: 'string'},
               {name: 'chamado', type: 'int'},
               {name: 'terceirizada', type: 'int'},
               {name: 'terceirizada_string', type: 'string'},
               {name: 'motivo', type: 'string'},
            ]);

        return this._fields;
    }
});
