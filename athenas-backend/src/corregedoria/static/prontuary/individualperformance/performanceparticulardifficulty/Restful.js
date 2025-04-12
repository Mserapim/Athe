Ext._define('corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailPerformanceParticularDifficulty',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.performanceparticulardifficulty.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons" },
                {type: "integer", name: "employeelocation" },
                {type: "string", name: "employeelocation_description" },
                {type: "integer", name: "used_edital" },
                {type: "string", name: "used_edital_unicode" },
                {type: "int", name: "score" },
                {type: "int", name: "total_days" },
            ]);

        return this._fields;
    }
});
