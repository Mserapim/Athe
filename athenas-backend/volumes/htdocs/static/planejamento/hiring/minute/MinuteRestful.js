Ext._define('planning.hiring.minute.MinuteRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinute',


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

        this.doRequest(this.getRoute('renderer_document', pk, 'GET', {
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.document);
                    else
                        core.invokeCallback((emptyFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function(xhr) {
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponível no momento.');
                },
                callback: function() {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.minute.MinuteRestful.superclass.getFields.call(this, cfg).concat([
                { name: "icons" },
                { type: "string", name: "minute_object" },
                { type: "date", name: "begin_validity", dateFormat: "d/m/Y" },
                { type: "int", name: "modified_by", useNull: true },
                { type: "string", name: "modified_by_unicode" },
                { type: "float", name: "total_amount", useNull: true },
                { type: "string", name: "official_diary" },
                { type: "string", name: "parent_process" },
                { type: "date", name: "end_validity", dateFormat: "d/m/Y" },
                { type: "date", name: "created_at", dateFormat: "d/m/Y H:i" },
                { type: "date", name: "signature_date", dateFormat: "d/m/Y" },
                { type: "date", name: "modified_at", dateFormat: "d/m/Y H:i" },
                { type: "string", name: "number" },
                { type: "int", name: "created_by", useNull: true },
                { type: "string", name: "created_by_unicode" },
                { type: "string", name: "notice_number" },
                { type: "int", name: "management_organ", useNull: true },
                { type: "string", name: "management_organ_unicode" },
                { type: "date", name: "publication_date", dateFormat: "d/m/Y" },
                { type: "int", name: "adhesions_quantity", useNull: true },
                { type: "string", name: "process_number" },
                { type: "string", name: "object_execution" },
                { type: "string", name: "bidding_type" },
                { type: "int", name: "days_for_notice" },
                { type: "int", name: "status", useNull: true },
                { type: "int", name: "provider" },  // Contratados
                { type: "int", name: "enterprise_provider" },  // Estrutura Corporativa
                { type: "string", name: "main_minutesupervisors" },  // Fiscais
            ]);
        }

        return this._fields;
    }
});
