Ext._define('planning.hiring.minuteitem.MinuteItemRestful', {
    extend: 'core.Restful',

    resource: 'PHMMinuteItem',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = planning.hiring.minuteitem.MinuteItemRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "minute", useNull: true},
                {type: "string", name: "minute_unicode"},
                {type: "string", name: "description"},
                {type: "string", name: "description_without_tags"},
                {type: "int", name: "parent", useNull: true},
                {type: "string", name: "parent_unicode"},
                {type: "int", name: "unit_measure", useNull: true},
                {type: "string", name: "unit_measure_display"},
                {type: "float", name: "quantity"},
                {type: "float", name: "unitary_value", useNull: true},
                {type: "float", name: "total_value", useNull: true},
                {type: "string", name: "group"},
                {type: "string", name: "line"},
                {type: "float", name: "item_balance", useNull: true},
                {type: "string", name: "brand", useNull: true},
                {type: "int", name: "created_by", useNull: true},
                {type: "string", name: "created_by_unicode"},
                {type: "date", name: "created_at", dateFormat: "d/m/Y H:i"},
                {type: "int", name: "modified_by", useNull: true},
                {type: "string", name: "modified_by_unicode"},
                {type: "date", name: "modified_at", dateFormat: "d/m/Y H:i"},
                {type: "bool", name: "generate_agreement", useNull: true},
                {type: "int", name: "status", useNull: true},
                {type: "string", name: "status_display"},
            ]);

        return this._fields;
    }
});
