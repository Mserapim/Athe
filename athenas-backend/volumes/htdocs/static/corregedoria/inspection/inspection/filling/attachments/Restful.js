Ext._define('corregedoria.inspection.inspection.filling.attachments.Restful', {
    extend: 'core.Restful',

    resource: 'INSPECTIONAttachments',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.inspection.inspection.filling.attachments.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "description"},
                {type: "string", name: "action_number"},
                {type: "int", name: "attached_file"},
                {type: "string", name: "attached_file_unicode"},
                {type: "string", name: "area_display"},
                {type: "auto", name: "area"},
                {type: "string", name: "attachment_type_display"},
                {type: "auto", name: "attachment_type"},
            ]);

        return this._fields;
    }
});
