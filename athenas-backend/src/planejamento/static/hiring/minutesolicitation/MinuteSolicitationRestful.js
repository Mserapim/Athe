Ext._define('planning.hiring.minutesolicitation.MinuteSolicitationRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteSolicitation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minutesolicitation.MinuteSolicitationRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: "string",
                    name: "justification"
                },
                {
                    type: "int",
                    name: "modified_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "modified_by_unicode"
                },
                {
                    type: "int",
                    name: "created_by",
                    useNull: true
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                },
                {
                    type: "string",
                    name: "situation",
                    useNull: true
                },
                {
                    type: "string",
                    name: "situation_display",
                    useNull: true
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "date",
                    name: "modified_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "string",
                    name: "number",
                    useNull: true
                },
                {
                    type: "int",
                    name: "minute",
                    useNull: true
                },
                {
                    type: "string",
                    name: "minute_unicode"
                },
                {
                    type: "string",
                    name: "edoc",
                    useNull: true
                },
                {
                    type: "string",
                    name: "edoc_display",
                }
            ]);

        return this._fields;
    }
});
