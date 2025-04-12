Ext._define('rh.dayoff.groupperiod.Restful', {
    extend: 'core.Restful',

    resource: 'DAYOFFGroupPeriod',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.dayoff.groupperiod.Restful.superclass.getFields.call(this, cfg).concat([
                { name: "created_by", type: "int", useNull: true },
                { name: "created_by_unicode", type: "string" },
                { name: "modified_by", type: "int", useNull: true },
                { name: "modified_by_unicode", type: "string" },
                { name: "created_at", type: "date", dateFormat: "d/m/Y H:i" },
                { name: "modified_at", type: "date", dateFormat: "d/m/Y H:i" },
                { name: "title", type: "string" },
                { name: "period", type: "int", useNull: true },
                { name: "start_date_book", type: "date", dateFormat: "d/m/Y" },
                { name: "end_date_book", type: "date", dateFormat: "d/m/Y" },
                { name: "homologation_date", type: "date", dateFormat: "d/m/Y" },
                { name: "publication_date", type: "date", dateFormat: "d/m/Y" },
                { name: "start_date_fruition", type: "date", dateFormat: "d/m/Y" },
                { name: "end_date_fruition", type: "date", dateFormat: "d/m/Y" },
                { name: "start_date_automatic_usufruct", type: "date", dateFormat: "d/m/Y" },
                { name: "end_date_automatic_usufruct", type: "date", dateFormat: "d/m/Y" },
                { name: "configuration", type: "int", useNull: true },
                { name: "configuration_unicode", type: "string" },
                { name: "blocked", type: "bool" },
                { name: "year_reference", type: "int", useNull: true },
                { name: "attachment", type: "int", useNull: true },
                { name: "attachment_unicode", type: "string" },
                { name: "icons", type: "auto" },
                { name: "start_date_acquisition", type: "date", dateFormat: "d/m/Y" },
                { name: "end_date_acquisition", type: "date", dateFormat: "d/m/Y" },
                { name: "redo_automatic_book", type: "bool" },
            ]);

        return this._fields;
    },

    _process: function (params, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function (message) {
                Ext.Msg.show({
                    title: 'Processando',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        };

        this.doRequest(this.getRoute(
            params.actionCustom,
            null,
            'POST',
            {
                params: params,
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst);
                    }
                    else
                        core.invokeCallback((emptyFailure || { fn: Ext.emptyFn }), rst.message);
                },
                failure: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);
                    core.invokeCallback((cbFailure || emptyFailure), 'Recurso indisponivel no momento.');
                },
                callback: function () {
                    core.invokeCallback((cbCallback || { fn: Ext.emptyFn }));
                }
            }
        ));
    },
});
