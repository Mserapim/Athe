Ext._define('common.document_access.legalprerogative.Restful', {
    extend: 'core.Restful',

    resource: 'DALegalPrerogative',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = common.document_access.legalprerogative.Restful.superclass.getFields.call(this, cfg).concat([
                { name: "title", type: "string" },
                { name: "description", type: "string" },
                { name: "control_type", type: "int", useNull: true },
                { name: "control_type_unicode", type: "string" },
                { name: "created_by", type: "int", useNull: true },
                { name: "created_by_unicode", type: "string" },
                { name: "created_at", type: "date", dateFormat: "d/m/Y H:i" },
                { name: "modified_by", type: "int", useNull: true },
                { name: "modified_by_unicode", type: "string" },
                { name: "modified_at", type: "date", dateFormat: "d/m/Y H:i" },
                { name: "enabled", type: "bool" },
            ]);
        }

        return this._fields;
    }
});
