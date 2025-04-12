Ext._define('planning.hiring.minuteitem.MinuteItemComplementaryDescriptionRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteItemComplementaryDescription',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.minuteitem.MinuteItemComplementaryDescriptionRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "minuteitem", useNull: true},
                {type: "string", name: "minuteitem_unicode"},
                {type: "string", name: "characteristic"},
                {type: "string", name: "description"}
            ]);
        }

        return this._fields;
    }
});
