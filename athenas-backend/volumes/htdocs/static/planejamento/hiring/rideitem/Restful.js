Ext._define('planning.hiring.rideitem.Restful', {
    extend: 'core.Restful',

    resource: 'PHMRideItem',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.rideitem.Restful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "int",
                    name: "ride"
                },
                {
                    type: "string",
                    name: "ride_unicode"
                },
                {
                    type: "int",
                    name: "group"
                },
                {
                    type: "int",
                    name: "line"
                },
                {
                    type: "int",
                    name: "item"
                },
                {
                    type: "string",
                    name: "item_unicode"
                },
                {
                    type: "float",
                    name: "amount"
                },
                {
                    type: "string",
                    name: "unitary_value"
                },
                {
                    type: "string",
                    name: "total_value"
                },
                {
                    type: "string",
                    name: "justification"
                },
                {
                    type: "int",
                    name: "status"
                },
                {
                    type: "string",
                    name: "status_display"
                }
            ]);

        return this._fields;
    }
});
