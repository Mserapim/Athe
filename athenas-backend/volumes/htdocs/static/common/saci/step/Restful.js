
Ext._define('common.saci.step.Restful', {
    extend: 'core.Restful',

    resource: 'SACIStepRestful',


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
            this._fields = common.saci.step.Restful.superclass.getFields.call(this, cfg).concat([

                {
                    type: "int",
                    name: "origin",
                    useNull: true
                },
                {
                    type: "string",
                    name: "origin_unicode"
                },

                {
                    type: "int",
                    name: "destination",
                    useNull: true
                },
                {
                    type: "string",
                    name: "destination_unicode"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },

            ]);

        return this._fields;
    }
});
