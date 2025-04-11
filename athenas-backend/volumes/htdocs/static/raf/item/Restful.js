Ext._define('raf.item.Restful', {
    extend: 'core.Restful',

    resource: 'RAFItem',

    enable: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'enable',
                pk,
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

    changeOrder: function(values, cbSuccess, cbFailure, cbCallback) {

        this.doRequest(
            this.getRoute(
                'change_order',
                false,
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
            this._fields = raf.item.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                {type: "integer", name: "quiz", useNull: true},
                {type: "string", name: "quiz_unicode"},
                {type: "string", name: "title"},
                {type: "bool", name: "activated"},
                {type: "bool", name: "cnmp"},
                {type: "integer", name: "number_order", useNull: true}
            ]);

        return this._fields;
    }
});
