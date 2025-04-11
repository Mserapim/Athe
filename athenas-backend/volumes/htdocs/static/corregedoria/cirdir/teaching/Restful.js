Ext._define('corregedoria.cirdir.teaching.Restful', {
    extend: 'core.Restful',

    resource: 'CIRDIRTeaching',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.cirdir.teaching.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "discipline" },
                {type: "string", name: "discipline_unicode" },
                {type: "int", name: "institution" },
                {type: "string", name: "institution_unicode" },
                {type: "int", name: "work_hours" },
                {type: "date", name: "start_date", dateFormat: "d/m/Y"},
                {type: "date", name: "end_date", dateFormat: "d/m/Y"},
                {type: "bool", name: "authorization_teaching" },
                {type: "int", name: "period" },
                {type: "int", name: "modality" },
                {type: "auto", name: "icons" },
            ]);

        return this._fields;
    }
});
