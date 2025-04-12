Ext._define('corregedoria.prontuary.career.designation.designationcumulation.attachments.Restful', {
    extend: 'core.Restful',

    resource: 'PRONTUARYAttachmentsDetailDesignationCumulation',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = corregedoria.prontuary.career.designation.designationcumulation.attachments.Restful.superclass.getFields.call(this, cfg).concat([
                {type: "string", name: "description"},
                {type: "int", name: "attached_file"},
                {type: "string", name: "attached_file_unicode"},
            ]);

        return this._fields;
    }
});
