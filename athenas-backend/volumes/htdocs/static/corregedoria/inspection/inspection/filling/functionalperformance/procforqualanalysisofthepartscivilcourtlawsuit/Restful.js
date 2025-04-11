Ext._define('corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartscivilcourtlawsuit.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONProcForQualAnalysisOfThePartsCivilCourtLawsuit',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.functionalperformance.procforqualanalysisofthepartscivilcourtlawsuit.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "action_type"},
                {type: "string", name: "action_type_title"},
                {type: "string", name: "action_type_unicode"},
                {type: "string", name: "action_number"},
                {type: "int", name: "part_type"},
                {type: "string", name: "part_type_title"},
                {type: "string", name: "report"},
                {type: "auto", name: "report_score"},
                {type: "string", name: "basis"},
                {type: "auto", name: "basis_score"},
                {type: "string", name: "proof"},
                {type: "auto", name: "proof_score"},
                {type: "string", name: "convincily"},
                {type: "auto", name: "convincily_score"},
                {type: "string", name: "redaction"},
                {type: "auto", name: "redaction_score"},
                {type: "auto", name: "score"},
                {type: "string", name: "observation"},
            ]);

        return this._fields;
    }
});
