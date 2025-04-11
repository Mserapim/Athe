/**
 *
 **/
Ext._define('adm.patrimonio.baixa.ItemBaixaRestful', {
    extend: 'core.Restful',

    resource: 'PATItemBaixa',

    importFromInputNotes: function(params, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'import_from_inputnotes',
                false,
                'POST',
                {
                    params: params,
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

    getFields: function() {
        return adm.patrimonio.baixa.ItemBaixaRestful.superclass.getFields().concat([
            {name: "icons", type: 'auto'},
            {"name": "patrimonio_plaqueta", type: 'string'},
            {name: "patrimonio_unicode", type: 'string'},
            {name: "patrimonio", type: 'int'},
            {name: "conservacao", type: 'string'},
            {name: "valor_atual", type: 'float'},
            {name: "valor_baixa", type: 'float'},
            {name: "avaliacao", type: 'float'},
            {name: 'data_tombo', type: 'date', dateFormat: 'd/m/Y'},
            {name: "observacao", type: 'string'}
        ]);
    }
});
