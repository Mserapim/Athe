Ext._define('corregedoria.prontuary.individualperformance.exerciseinrole.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailExerciseInRole',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.exerciseinrole.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons" },
                {type: "string", name: "exercise" },
                {type: "string", name: "role" },
                {type: "date", name: "date_initial", dateFormat: "d/m/Y" },
                {type: "date", name: "date_final", dateFormat: "d/m/Y" },
                {type: "string", name: "act_initial" },
                {type: "string", name: "act_final" },
                {type: "integer", name: "used_edital" },
                {type: "string", name: "used_edital_unicode" },
                {type: "int", name: "validated" },
                {type: "int", name: "score" },
            ]);

        return this._fields;
    }
});
