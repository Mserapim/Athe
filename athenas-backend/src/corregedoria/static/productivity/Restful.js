Ext._define('corregedoria.productivity.Restful', {
    extend: 'core.Restful',

    resource: 'CORREGEDORIAProductivity',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.productivity.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "productivity"},
                {type: "string", name: "productivity_display"},
                {type: "int", name: "score_table"},
                {type: "string", name: "score_table_display"},
            ]);

        return this._fields;
    }
});
