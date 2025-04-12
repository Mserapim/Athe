Ext._define('common.document_access.log.Restful', {
    extend: 'core.Restful',

    resource: 'DALog',

    rendererDocument: function (pk, cbSuccess, cbFailure, cbCallback) {
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
            'GET', {
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

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = common.document_access.log.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "pk", type: "int", useNull: true},
                {name: "unicode", type: "string"},
                {name: "signed_by", type: "int", useNull: true},
                {name: "signed_by_unicode", type: "string"},
                {name: "signed_at", type: "date", dateFormat: "d/m/Y H:i"},
                {name: "control", type: "int", useNull: true},
                {name: "control_unicode", type: "string"},
                {name: "control_type", type: "int", useNull: true},
                {name: "control_type_unicode", type: "string"},
                {name: "log_type", type: "int"},
                {name: "log_type_display", type: "string"},
                {name: "description", type: "string"},
            ]);

        return this._fields;
    }
});
