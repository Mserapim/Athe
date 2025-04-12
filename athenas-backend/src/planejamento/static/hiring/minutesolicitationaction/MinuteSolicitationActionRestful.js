
Ext._define('planning.hiring.minutesolicitationaction.MinuteSolicitationActionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitationAction',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitationaction.MinuteSolicitationActionRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "unicode"
                },
                {
                    type: "string",
                    name: "date"
                },
                {
                    type: "string",
                    name: "observation"
                }

            ]);

        return this._fields;
    }
});
