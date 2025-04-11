/**
 *
 **/
Ext._define('adm.patrimonio.movimento.LogStatusRestful', {
    extend: 'core.Restful',

    resource: 'PATMovimentoLogStatus',

    getFields: function() {
        if(!this._fields)
            this._fields = adm.patrimonio.movimento.LogStatusRestful.superclass.getFields.call(this).concat([
                {name: 'icons', type: 'auto'},
                {name: 'atribuido_por', type: 'int'},
                {name: 'atribuido_por_unicode', type: 'string'},
                {name: 'movimento', type: 'int'},
                {name: 'comentario', type: 'string'},
                {name: 'status', type: 'int'},
                {name: 'status_display', type: 'string'},
                {name: 'atribuido', type: 'date', dateFormat: 'd/m/Y H:i'}
            ]);

        return this._fields;
    },

    manifestateStatusChange: function(params, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'manifestate_status_change',
                false,
                'PUT',
                {
                    params: {
                        pkset: params.pkset,
                        status: params.status,
                        comentario: params.comentario
                    },
                    scope: this,
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    },
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    }
                }
            )
        );
    }
});
