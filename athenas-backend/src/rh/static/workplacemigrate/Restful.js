Ext._define('rh.workplacemigrate.Restful', {
    extend: 'core.Restful',

    resource: 'RHWorkplaceMigrate',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.workplacemigrate.Restful.superclass.getFields.call(this, cfg).concat([
                { type: 'int', name: 'type_of_migrate', useNull: true },
                { type: 'string', name: 'type_of_migrate_display' },
                { type: 'date', name: 'modified_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'modified_by', useNull: true },
                { type: 'string', name: 'modified_by_unicode' },
                { type: 'date', name: 'created_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'created_by', useNull: true },
                { type: 'string', name: 'created_by_unicode' },
                { type: 'int', name: 'workplace', useNull: true },
                { type: 'string', name: 'workplace_unicode' },
                { type: 'int', name: 'workplace_destiny', useNull: true },
                { type: 'string', name: 'workplace_destiny_unicode' },
                { type: 'int', name: 'publication', useNull: true },
                { type: 'string', name: 'publication_unicode' },
                { type: 'string', name: 'description' },
                { type: 'date', name: 'signed_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'signed_by', useNull: true },
                { type: 'string', name: 'signed_by_unicode' },
            ]);

        return this._fields;
    },

    performMigration: function (pkset, cbSuccess, cbFailure, cbCallback) {
        var emptyFailure = {
            fn: function (message) {
                Ext.Msg.show({
                    title: 'Migração de Lotação/Órgão',
                    icon: Ext.Msg.WARNING,
                    buttons: Ext.Msg.OK,
                    msg: message
                });
            }
        };

        this.doRequest(this.getRoute(
            'perform_migration',
            null,
            'PUT',
            {
                params: {
                    pkset: pkset
                },
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success)
                        core.invokeCallback((cbSuccess || { fn: Ext.emptyFn }), rst.message);
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
});
