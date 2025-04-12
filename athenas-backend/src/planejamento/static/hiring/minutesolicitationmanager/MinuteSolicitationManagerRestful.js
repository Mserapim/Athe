Ext._define('planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationManager',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerRestful.superclass.getFields.call(this, cfg).concat([
                { type: "string",  name: "justification" }, 
                { type: "int",     name: "modified_by",  useNull: true }, 
                { type: "string",  name: "modified_by_unicode" }, 
                { type: "int",     name: "created_by",  useNull: true }, 
                { type: "string",  name: "created_by_unicode" }, 
                { type: "string",  name: "situation", useNull: true }, 
                { type: "string",  name: "situation_display", useNull: true }, 
                { type: "date",    name: "created_at", dateFormat: "d/m/Y H:i" }, 
                { type: "date",    name: "modified_at", dateFormat: "d/m/Y H:i" }, 
                { type: "string",  name: "number", useNull: true }, 
                { type: "int",     name: "minute",  useNull: true }, 
                { type: "string",  name: "minute_unicode" }, 
                { type: "string",  name: "edoc", useNull: true },
                { type: "string",  name: "edoc_display", },
                { type: "string",  name: "minute_process_number_display" },
                { type: "string",  name: "main_supervisors_display" }, 
            ]);

        return this._fields;
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
            'GET', {
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((emptyFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },
});
