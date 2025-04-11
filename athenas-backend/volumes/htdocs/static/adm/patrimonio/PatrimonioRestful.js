/**
 *
 **/
Ext._define('adm.patrimonio.PatrimonioRestful', {
    extend: 'core.Restful',

    resource: 'PATPatrimonio',

    changeConsevation: function (pkset, conservation, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'change_consevation',
                false,
                'POST',
                {
                    params: {
                        pkset: pkset,
                        conservation: conservation
                    },
                    scope: this,
                    callback: function () { core.invokeCallback((cbCallback || core.voidCallback)); },
                    success: function (xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if (rst.success)
                            core.invokeCallback((cbSuccess || core.voidCallback), rst);
                        else
                            core.invokeCallback((cbFailure || core.voidCallback), rst.message);
                    },
                    failure: function () {
                        core.invokeCallback(
                            (cbFailure || core.voidCallback),
                            'Recurso indisponivel no momento.'
                        );
                    }
                }
            )
        );
    },

    save_observation: function (pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'save_observation',
                pk,
                'POST',
                {
                    params: values,
                    scope: this,
                    callback: function () {
                        core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                    },
                    success: function (xhr) {
                        var rst = Ext.decode(xhr.responseText);

                        if (rst.success)
                            core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst);
                        else
                            core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), rst.message);
                    },
                    failure: function () {
                        core.invokeCallback((cbFailure || { fn: Ext.emptyFn }), 'Recurso indisponivel no momento.');
                    }
                }
            )
        );
    },

    getFields: function () {
        return adm.patrimonio.PatrimonioRestful.superclass.getFields().concat([
            { "name": "icons", type: 'auto' },
            { "name": "item_entrada_unicode", type: 'string' },
            { "name": "item_entrada", type: 'int' },
            { "name": "localizacao_unicode", type: 'string' },
            { "name": "localizacao", type: 'int' },
            { "name": "responsavel_unicode", type: 'string' },
            { "name": "responsavel", type: 'int' },
            { "name": "utilizado_por_unicode", type: 'string' },
            { "name": "utilizado_por", type: 'int' },
            { "name": "plaqueta_unicode", type: 'string' },
            { "name": "plaqueta", type: 'string' },
            { "name": "especie", type: 'int' },
            { "name": "read_only", type: 'bool' },
            { "name": "especie_codigo", type: 'string' },
            { "name": "especie_unicode", type: 'string' },
            { "name": "conservacao", type: 'int' },
            { "name": "conservacao_display", type: 'string' },
            { "name": "observacao", type: 'string' },
            { "name": "nota_entrada", type: 'int' },
            { "name": "nota_entrada_cache_type", type: 'string' },
            { "name": "nota_baixa", type: 'int' },
            { "name": "nota_baixa_cache_type", type: 'string' },
            { "name": "utilizacao", type: 'int' },
            { "name": "utilizacao_display", type: 'string' },
            { "name": "descricao", type: 'string' },
            { "name": "valor_atual", type: 'float' },
            { "name": "valor_aquisicao", type: 'float' },
            { "name": "valor_base", type: 'float' },
            { "name": "depreciado", type: 'float' },
            { "name": "total_reavaliacao", type: 'float' },
            { "name": "data_baixa", type: 'date', dateFormat: 'd/m/Y' },
            { "name": "data_tombo", type: 'date', dateFormat: 'd/m/Y' },
            { "name": "prazo_garantia", type: 'date', dateFormat: 'd/m/Y' },
            { "name": "status_baixa", type: 'string' },
        ]);
    },

    rendererDocument: function (pk, cbSuccess, cbFailure, cbCallback) {

        // console.log('render de chamado');
        var emptyFailure = {
            fn: function (message) {
                Ext.Msg.show({
                    title: 'Buscando documento',
                    msg: message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        };

        this.doRequest(this.getRoute(
            'renderer_document',
            pk,
            'GET',
            {
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((emptyFailure || { fn: Ext.emptyFn }), rst.message);

                },
                failure: function (xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function () {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },
});
