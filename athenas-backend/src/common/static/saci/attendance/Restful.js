Ext._define('common.saci.attendance.Restful', {
    extend: 'core.Restful',

    resource: 'SACIAttendanceRestful',

    accessControl: function(pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'access_control',
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

    movement: function(pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'movement',
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

    finalize: function(pk, values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'finalize',
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

    afterGenerateLawsuit: function(values, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'after_generate_lawsuit',
                false,
                'POST',
                {
                    scope: this,
                    params: values,
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

    checkToSign: function(pk, cbSuccess, cbFailure, cbCallback) {
        this.doRequest(
            this.getRoute(
                'check_to_sign',
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

    sign: function(pkset, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function(message) {
                Ext.Msg.show({
                    title: 'Finalizando documento',
                    msg: message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        };

        this.doRequest(this.getRoute(
            'sign',
            false,
            'POST',
            {
                params: {
                    pkset: pkset
                },
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
            this._fields = common.saci.attendance.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'icons'},
                { type: "int",    name: "movement", useNull: true },
                { type: "int",    name: "person", useNull: true },
                { type: "string", name: "person_unicode" },
                { type: "int",    name: "destination", useNull: true },
                { type: "string", name: "destination_unicode" },
                { type: "int",    name: "represented", useNull: true },
                { type: "string", name: "represented_unicode" },
                { type: "bool",   name: "contains_represented" },
                { type: "bool",   name: "competence_others" },
                { type: "string", name: "feedback" },
                { type: "string", name: "story" },
                { type: "string", name: "subject" },
                { type: "date",   name: "created_at", dateFormat: "d/m/Y H:i" },
                { type: "date",   name: "signed_at", dateFormat: "d/m/Y H:i" },
                { type: "string", name: "signed_at_unicode" },
                { type: "date",   name: "modified_at", dateFormat: "d/m/Y H:i" },
                { type: "int",    name: "created_by", useNull: true },
                { type: "string", name: "created_by_unicode" },
                { type: "int",    name: "modified_by", useNull: true },
                { type: "string", name: "modified_by_unicode" },
                { type: "int",    name: "protocol", useNull: true },
                { type: "string", name: "protocol_unicode" },
                { type: "int",    name: "department", useNull: true },
                { type: "string", name: "department_unicode" },
                { type: "int",    name: "typology", useNull: true },
                { type: "string", name: "typology_unicode" },
                { type: "bool",   name: "confidential" },

                // Controle de Acesso (app document_access)
                { type: "int",    name: "control" },
                { type: "int",    name: "control_type" },
                { type: "bool",   name: "can_read" },
            ]);

        return this._fields;
    }
});
