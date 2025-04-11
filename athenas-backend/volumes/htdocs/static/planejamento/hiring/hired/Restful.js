Ext._define('planning.hiring.hired.Restful', {
    extend: 'core.Restful',

    resource: 'PHAHired',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.agreement.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "agreement"
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
