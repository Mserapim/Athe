
Ext._define('planning.hiring.agreementannotation.Restful', {
    extend: 'core.Restful',

    resource: 'PHAAgreementAnnotation',

    getFields: function (cfg) {
        if (!this._fields)
            this._fields = planning.hiring.agreementannotation.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int",name: "kind"},
                {type: "string",name: "kind_display"},
                {type: "string",name: "note"},
                {type: "string",name: "date"},
                {type: "string",name: "schedule_date"},
                {type: "bool", name: "schedule"},
                {type: "int",name: "agreement"},
                {type: "string",name: "agreement_unicode"}
            ]);

        return this._fields;
    }
});
