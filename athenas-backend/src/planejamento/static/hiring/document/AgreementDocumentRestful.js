Ext._define('planning.hiring.document.AgreementDocumentRestful', {
    extend: 'core.Restful',

    resource: 'PHAgreementDocument',

    getFields: function(cfg) {
        if (!this._fields) {
            this._fields = planning.hiring.document.AgreementDocumentRestful.superclass.getFields.call(this, cfg).concat([
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
                    name: 'agreement'
                }
            ]);
        }
        return this._fields;
    }
});