
Ext._define('planning.hiring.agreementannotation.MinuteAnnotationRestful', {
    extend: 'core.Restful',

    resource: 'PHAMinuteAnnotation',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.agreementannotation.MinuteAnnotationRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int",name: "kind"},
                {type: "string",name: "kind_display"},
                {type: "string",name: "note"},
                {type: "string",name: "date"},
                {type: "string",name: "schedule_date"},
                {type: "bool", name: "schedule"},
                {type: "int",name: "minute"},
                {type: "string",name: "minute_unicode"}
            ]);

        return this._fields;
    }
});
