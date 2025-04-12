/**
 *
 **/
Ext._define('common.siatu.chamado.transferencia.Restful', {
    extend: 'core.Restful',

    resource: 'SiatuTransferencia',

    getFields: function() {
        if(!this._fields)
            this._fields = common.siatu.chamado.transferencia.Restful.superclass.getFields.call(this).concat([
               {name: 'data_pedido', type: 'string'},
               {name: 'motivo', type: 'string'},
               {name: 'data_aceite', type: 'string'},
               {name: 'aceito_por', type: 'string'},
               {name: 'pedido_por', type: 'string'},
               {name: 'cancelado', type: 'bool'},
            ]);

        return this._fields;
    }
});
