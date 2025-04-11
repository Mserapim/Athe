Ext._define('common.saci.attachment.Restful', {
    extend: 'core.Restful',

    resource: 'SACIAttachmentRestful',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = common.saci.attachment.Restful.superclass.getFields.call(this, cfg).concat([
                // {
                //     type: "auto",
                //     name: "icons"
                // },
                {
                    type: "int",
                    name: "attendance",
                    useNull: true
                },
                {
                    type: "string",
                    name: "attendance_unicode"
                },
                {
                    type: "int",
                    name: "file_descriptor",
                    useNull: true
                },
                {
                    type: "string",
                    name: "file_descriptor_unicode"
                },
                {
                    type: "string",
                    name: "created_by_unicode"
                },
                {
                    type: "date",
                    name: "created_at",
                    dateFormat: "d/m/Y H:i"
                },
                {
                    type: "string",
                    name: "title"
                }
            ]);

        return this._fields;
    }
});
