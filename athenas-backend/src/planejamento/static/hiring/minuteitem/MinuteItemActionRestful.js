
Ext._define('planning.hiring.minuteitem.MinuteItemActionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteItemAction',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minuteitem.MinuteItemActionRestful.superclass.getFields.call(this, cfg).concat([
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
