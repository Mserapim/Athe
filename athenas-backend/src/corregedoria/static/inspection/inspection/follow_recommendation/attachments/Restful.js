Ext._define('corregedoria.inspection.inspection.follow_recommendation.attachments.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONDeadlineRecommendationAttachments',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.follow_recommendation.attachments.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "int", name: "deadlinerecommendation"}, //Adicionando este campo porque o modelo 
                // Attachment não aceita null que seja null.
                {type: "string", name: "description"},
                {type: "int", name: "attached_file"},
                {type: "string", name: "attached_file_unicode"},
            ]);

        return this._fields;
    }
});
