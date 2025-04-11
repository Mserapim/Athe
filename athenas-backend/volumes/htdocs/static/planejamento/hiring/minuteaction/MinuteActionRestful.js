
Ext._define('planning.hiring.minuteaction.MinuteActionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteAction',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minuteaction.MinuteActionRestful.superclass.getFields.call(this, cfg).concat([
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
