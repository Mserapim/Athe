Ext._define('corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONProcessesForAnalysisPerformanceInAudiences',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.regularityofservices.processesforanalysisperformanceinaudiences.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "action_type"},
                {type: "string", name: "action_type_title"},
                {type: "string", name: "action_type_unicode"},
                // {type: "string", name: "action_type_display"},
                // {type: "int", name: "action_type"},
                {type: "string", name: "action_number"},
                {type: "int", name: "audience_type"},
                {type: "string", name: "audience_type_display"},
                {type: "bool", name: "intimation"},
                {type: "bool", name: "presence"},
                {type: "bool", name: "questions"},
                {type: "bool", name: "oral_manifestation"},
            ]);

        return this._fields;
    }
});
