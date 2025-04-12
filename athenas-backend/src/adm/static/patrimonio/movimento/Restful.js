Ext._define('adm.patrimonio.movimento.Restful', {
    extend: 'core.Restful',

    resource: 'PATMovimento',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.movimento.Restful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'id', type: 'int'},
                {name: 'identificacao', type: 'string'},
                {name: 'origem', type: 'int'},
                {name: 'origem_unicode', type: 'string'},
                {name: 'destino', type: 'int'},
                {name: 'destino_unicode', type: 'string'},
                {name: 'movimentado_por', type: 'int'},
                {name: 'movimentado_por_unicode', type: 'string'},
                {name: 'recebido_por', type: 'int'},
                {name: 'recebido_por_unicode', type: 'string'},
                {name: 'responsavel_destino', type: 'int'},
                {name: 'responsavel_destino_unicode', type: 'string'},
                {name: 'validado_por', type: 'int'},
                {name: 'validado_por_unicode', type: 'string'},
                {name: 'status_display', type: 'string'},
                {name: 'status', type: 'int'},
                {name: 'assinatura_entrega', type: 'string'},
                {name: 'assinatura_recebimento', type: 'string'},
                {name: 'assinatura_patrimonio', type: 'string'},
                {name: 'autorizado', type: 'auto'},
                {name: 'has_notifications', type: 'bool'},
            ]);

        return this._fields;
    }
});
