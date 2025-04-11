Ext._define('planning.hiring.document.ValueDocumentRestful', {
    extend: 'core.Restful',

    resource: 'PHValueDocument',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.document.ValueDocumentRestful.superclass.getFields.call(this, cfg).concat([
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
                    name: 'value'
                }
            ]);
        }
        return this._fields;
    }
});