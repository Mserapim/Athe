
Ext._define('planning.hiring.meterage.Restful', {
    extend: 'core.Restful',

    resource: 'PHAMeterage',

    dispatch: function(pks, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'dispatch',
                pks,
                'POST',
                {
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },

    pay: function(pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'pay',
                pk,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function() {
                        core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                    },
                    success: function(xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if(rst.success)
                            core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst);
                        else
                            core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), rst.message);
                    },
                    failure: function() {
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.meterage.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    name: "icons"
                },
                {
                    type: "int",
                    name: "nota_empenho"
                },
                {
                    type: "string",
                    name: "nota_empenho_display"
                },
                {
                    type: "float",
                    name: "valor"
                },
                {
                    type: "string",
                    name: "nota_fiscal"
                },
                {
                    type: "string",
                    name: "inicio_periodo_referencia"
                },
                {
                    type: "string",
                    name: "fim_periodo_referencia"
                },
                {
                    type: "string",
                    name: "periodo_display"
                },
                {
                    type: "string",
                    name: "observacao"
                },
                {
                    type: "int",
                    name: "user"
                },
                {
                    type: "string",
                    name: "user_display"
                },
                {
                    type: "string",
                    name: "ordem_bancaria"
                },
            ]);

        return this._fields;
    }
});
