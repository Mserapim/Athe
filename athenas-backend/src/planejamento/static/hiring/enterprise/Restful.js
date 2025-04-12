Ext._define('planning.hiring.enterprise.Restful', {
    extend: 'core.Restful',

    resource: 'PHEEnterprise',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.enterprise.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "person"
                },
                {
                    type: "string",
                    name: "person_unicode"
                },
                {
                    type: "bool",
                    name: "apply"
                },
                {
                    type: "int",
                    name: "motive"
                },
                {
                    type: "int",
                    name: "motive_choice"
                },
                {
                    type: "string",
                    name: "motive_unicode"
                }
            ]);

        return this._fields;
    }
});
