Ext._define('corregedoria.inspection.inspection.filling.procuratorate.procforqualanalysisofthepartsprocuratorate.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONProcForQualAnalysisOfThePartsProcuratorate',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.procuratorate.procforqualanalysisofthepartsprocuratorate.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "action_type"},
                {type: "string", name: "action_type_title"},
                {type: "string", name: "action_type_unicode"},
                {type: "string", name: "action_number"},
                {type: "int", name: "part_type"},
                {type: "string", name: "part_type_title"},
                {type: "string", name: "report"},
                {type: "string", name: "basis"},
                {type: "string", name: "proof"},
                {type: "string", name: "convincily"},
                {type: "string", name: "redaction"},
                {type: "auto", name: "score"},
                {type: "string", name: "observation"},
            ]);

        return this._fields;
    }
});
