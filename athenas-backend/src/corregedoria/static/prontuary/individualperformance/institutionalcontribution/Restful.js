Ext._define('corregedoria.prontuary.individualperformance.institutionalcontribution.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYDetailInstitutionalContribution',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.individualperformance.institutionalcontribution.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "score" },
                {type: "string", name: "contribution" },
            ]);

        return this._fields;
    }
});
