Ext._define('raf.adjustment.BaseRestful', {
    extend: 'core.Restful',

    resource: 'RAFActivityAdjustment',

    action: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'action',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    save: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'save',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    newAmount: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'newAmount',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    close: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'close',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    undoAction: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'undoAction',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    sendAction: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'sendAction',
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
                        core.invokeCallback((cbFailure || {fn: Ext.emptyFn}), 'Recurso indisponível no momento.');
                    }
                }
            )
        );
    },

    rendererDocument: function(pk, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function(message) {
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
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    if(rst.success)
                        core.invokeCallback((cbSuccess || {fn: Ext.emptyFn}), rst.document);
                    else
                        core.invokeCallback((emptyFailure || {fn: Ext.emptyFn}), rst.message);

                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || {fn: Ext.emptyFn}));
                }
            }
        ));
    },

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.activity.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "status"},
                {name: "icons"},
                {type: 'bool', name: "conversation_in_box"},
                {type: "integer", name: "activity", useNull: true},
                {type: "string", name: "activity_unicode"},
                {type: "string", name: "unicode"},
                {type: "integer", name: "amount", useNull: true},
                {type: "integer", name: "amount_athenas", useNull: true},
                {type: "integer", name: "conversation", useNull: true},
                {type: "string", name: "activity_created_at", useNull: true},
                {type: "integer", name: "location", useNull: true},
                {type: "string", name: "initial_message"},
                {type: "integer", name: "situation"},
                {type: "integer", name: "activity_amount_submitted"},
                {type: "string", name: "workerlocation_unicode"},
                {type: "int", name: "quiz"},
                {type: "string", name: "quiz_unicode"},
                {type: "string", name: "item_unicode"},
                {type: "string", name: "subitem_unicode"},
            ]);

        return this._fields;
    }
});
