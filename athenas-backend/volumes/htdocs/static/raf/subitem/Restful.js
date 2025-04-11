Ext._define('raf.subitem.Restful', {
    extend: 'core.Restful',

    resource: 'RAFSubItem',

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

    copy_item: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'copy_item',
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

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.subitem.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                {type: "integer", name: "quiz", useNull: true},
                {type: "string", name: "quiz_unicode"},
                {type: "string", name: "title"},
                {type: "string", name: "description"},
                {type: "bool", name: "activated"},
                {type: "bool", name: "cnmp"},
                {type: "bool", name: "manual_amount"},
                {type: "string", name: "productivity_display"},
                {type: "string", name: "productivity"},
                {type: "bool", name: "blocked"},
                {type: "integer", name: "number_order", useNull: true},
                // {type: "string", name: "list_taxonomy", useNull: true},
                {type: "string", name: "typesubitem_display"},
                {type: "string", name: "typesubitem"},
            ]);

        return this._fields;
    }
});
