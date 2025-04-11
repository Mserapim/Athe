Ext._define('planning.hiring.document.DocumentRestful', {
    extend: 'core.Restful',

    resource: 'PHDocument',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.document.DocumentRestful.superclass.getFields.call(this, cfg).concat([
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
                }
            ]);
        }
        return this._fields;
    }
})