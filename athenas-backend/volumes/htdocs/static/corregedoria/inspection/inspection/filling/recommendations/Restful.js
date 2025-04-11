Ext._define('corregedoria.inspection.inspection.filling.recommendations.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONRecommendations',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.recommendations.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "recommendation"},
                {type: "string", name: "deadline_grid"},
                {type: "bool", name: "waiting_response"},
                {type: "date", name: "deadline", dateFormat: "d/m/Y",  useNull: true},
            ]);

        return this._fields;
    },

});
