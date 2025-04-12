Ext._define('judicial.secretary.Restful', {
    extend: 'core.Restful',

    resource: 'EJudSecretary',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = judicial.secretary.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "modified_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "modified_by_unicode"
                },
                {
                    type: "string",
                    name: "title"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "int",
                    name: "created_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                },
                {
                    type: "int",
                    name: "location",
                    useNull: true
                },
                {
                    type: "string",
                    name: "location_unicode"
                }
            ]);

        return this._fields;
    }
});
