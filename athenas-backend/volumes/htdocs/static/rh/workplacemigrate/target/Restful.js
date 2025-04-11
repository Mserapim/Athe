Ext._define('rh.workplacemigrate.target.Restful', {
    extend: 'core.Restful',

    resource: 'RHTargetWorkplaceMigrate',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = rh.workplacemigrate.target.Restful.superclass.getFields.call(this, cfg).concat([
                { type: 'int', name: 'workplace_migrate', useNull: true },
                { type: 'string', name: 'workplace_migrate_unicode' },
                { type: 'int', name: 'type_of_target', useNull: true },
                { type: 'string', name: 'type_of_target_display' },
                { type: 'date', name: 'done_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'done_by', useNull: true },
                { type: 'string', name: 'done_unicode' },
                { type: 'date', name: 'modified_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'modified_by', useNull: true },
                { type: 'string', name: 'modified_by_unicode' },
                { type: 'date', name: 'created_at', dateFormat: 'd/m/Y H:i' },
                { type: 'int', name: 'created_by', useNull: true },
                { type: 'string', name: 'created_by_unicode' },
            ]);

        return this._fields;
    }
});
