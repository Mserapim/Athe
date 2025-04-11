Ext._define('raf.adjustment.dataadjustment.Restful', {
    extend: 'core.Restful',

    resource: 'RAFDataAdjustment',

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

    actionAll: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'action_all',
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

    get_data_process: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_data_process',
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

    get_data_process_add: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'get_data_process_add',
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

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = raf.adjustment.dataadjustment.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons"},
                {type: "auto", name: "operation"},
                {type: "auto", name: "operation_display"},
                {type: "auto", name: "source"},
                {type: "auto", name: "source_display"},
                {type: "auto", name: "process_number"},
                {type: "auto", name: "process_number_formatted"},
                {type: "auto", name: "date"},
                {type: "auto", name: "classification"},
                {type: "auto", name: "movement"},
                {type: "auto", name: "movement_title"},
                {type: "auto", name: "movement_unicode"},
                {type: "auto", name: "legalclass"},
                {type: "auto", name: "legalclass_title"},
                {type: "auto", name: "legalclass_unicode"},
                {type: "auto", name: "legalmatter"},
                {type: "auto", name: "legalmatter_title"},
                {type: "auto", name: "legalmatter_unicode"},
                {type: "auto", name: "situation"},
                {type: "auto", name: "initial_message"},
                {type: "auto", name: "activityadjustment_id"},
                {type: "string", name: "activity_unicode"},
                {type: "integer", name: "location", useNull: true},
                {type: "integer", name: "conversation", useNull: true},
                {type: 'bool', name: "conversation_in_box"},
                {type: 'string', name: "conversation_last_content"},
            ]);

        return this._fields;
    }
});
