Ext._define('corregedoria.scoretable.bandscoretable.Restful', {
    extend: 'core.Restful',

    resource: 'CORREGEDORIABandScoreTable',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.scoretable.bandscoretable.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "label"},
                {type: "auto", name: "initial_value", useNull: true},
                {type: "auto", name: "end_value", useNull: true},
                {type: "int", name: "score", useNull: true},
            ]);

        return this._fields;
    }
});
