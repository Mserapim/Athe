Ext._define('rh.dayoff.attachment.Restful', {
    extend: 'core.Restful',

    resource: 'DAYOFFAttachment',

    getFields: function(cfg) {
        if(!this._fields)
            this._fields = rh.dayoff.attachment.Restful.superclass.getFields.call(this, cfg).concat([
                {name: 'created_by',type: 'int',useNull: true},
                {name: 'created_by_unicode',type: 'string'},
                {name: 'modified_by',type: 'int',useNull: true},
                {name: 'modified_by_unicode',type: 'string'},
                {name: 'created_at',type: 'date',dateFormat: 'd/m/Y H:i'},
                {name: 'modified_at',type: 'date',dateFormat: 'd/m/Y H:i'},
                { name: 'file_descriptor', type: 'int', useNull: true },
                { name: 'file_descriptor_unicode', type: 'string' },
                { name: 'protocol', type: 'int', useNull: true },
                { name: 'protocol_unicode', type: 'string' },
                { name: 'publication', type: 'int', useNull: true },
                { name: 'publication_unicode', type: 'string' },
                { name: 'sei_url', type: 'string', useNull: true },
                { name: 'attachment_unicode', type: 'string' },
            ]);

        return this._fields;
    }
});
