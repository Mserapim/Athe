Ext._define('planning.hiring.corporatestructure.Restful', {
    extend: 'core.Restful',

    resource: 'PHECorporateStructure',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.corporatestructure.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "enterprise"
                },
                {
                    type: "string",
                    name: "enterprise_unicode"
                },
                {
                    type: "int",
                    name: "person"
                },
                {
                    type: "string",
                    name: "person_unicode"
                },
                {
                    type: "int",
                    name: "office"
                },
                {
                    type: "string",
                    name: "office_unicode"
                },
                {
                    type: "string",
                    name: "start_date"
                },
                {
                    type: "string",
                    name: "end_date"
                },
            ]);

        return this._fields;
    }
});
