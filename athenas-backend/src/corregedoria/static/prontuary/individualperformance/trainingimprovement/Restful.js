Ext._define('corregedoria.prontuary.individualperformance.trainingimprovement.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailTrainingImprovement',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.trainingimprovement.Restful.superclass.getFields.call(this, cfg).concat([
                {name: "icons" },
                {type: "string", name: "publication" },
                {type: "integer", name: "publication_type" },
                {type: "string", name: "publication_type_unicode" },
                {type: "date", name: "date_publication", dateFormat: "d/m/Y" },
                {type: "integer", name: "used_edital" },
                {type: "string", name: "used_edital_unicode" },
                {type: "int", name: "validated" },
                {type: "int", name: "score" },
            ]);

        return this._fields;
    }
});
