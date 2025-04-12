Ext._define('corregedoria.cirdir.InformationEvaluationRestful', {
    extend: 'core.Restful',

    resource: 'CIRDIRInformationEvaluation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.InformationEvaluationRestful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "code" },
                {type: "string", name: "unicode" },
            ]);

        return this._fields;
    }
});
