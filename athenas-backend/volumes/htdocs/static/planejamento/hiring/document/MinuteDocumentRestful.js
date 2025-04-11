Ext._define('planning.hiring.document.MinuteDocumentRestful', {
    extend: 'core.Restful',

    resource: 'PHMinuteDocument',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.document.MinuteDocumentRestful.superclass.getFields.call(this, cfg).concat([
                {
                    type: 'string',
                    name: 'title'
                },
                {
                    type: 'int',
                    name: 'file'
                },
                {
                    type: 'string',
                    name: 'filename'
                },
                {
                    type: 'string',
                    name: 'document_type'
                },
                {
                    type: 'int',
                    name: 'minute'
                }
            ]);
        }
        return this._fields;
    }
});