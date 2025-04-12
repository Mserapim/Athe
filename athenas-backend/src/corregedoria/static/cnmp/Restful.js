Ext._define('corregedoria.cnmp.Restful', {
    extend: 'core.Restful',

    resource: 'CNMPCommunication',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cnmp.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "auto", name: "icons"},
                {type: "int", name: "employee"},
                {type: "string", name: "employee_unicode"},
            ]);

        return this._fields;
    },

    rendererDocument: function(pk, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function(message) {
                Ext.Msg.show({
                    title: 'Buscando ...',
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
});
