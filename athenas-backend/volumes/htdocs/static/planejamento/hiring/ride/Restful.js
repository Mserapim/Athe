Ext._define('planning.hiring.ride.Restful', {
    extend: 'core.Restful',

    resource: 'PHMRide',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.ride.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "number"
                },
                {
                    type: "int",
                    name: "minute"
                },
                {
                    type: "string",
                    name: "minute_unicode"
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
                    name: "asking"
                },
                {
                    type: "string",
                    name: "asking_date"
                },
                {
                    type: "string",
                    name: "agreement_date"
                },
                {
                    type: "string",
                    name: "authorization_date"
                },
                {
                    type: "string",
                    name: "dispatch_number"
                },
            ]);

        return this._fields;
    }
});
