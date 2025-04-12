Ext._define('corregedoria.scoretable.Restful', {
    extend: 'core.Restful',

    resource: 'CORREGEDORIAScoreTable',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.scoretable.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "score_table"},
                {type: "string", name: "score_table_display"},
                {type: "string", name: "ordination"},
                {type: "date", name: "initial_validity", dateFormat: "d/m/Y"},
                {type: "date", name: "final_validity", dateFormat: "d/m/Y"},
                {type: "bool", name: "active"},
            ]);

        return this._fields;
    }
});
