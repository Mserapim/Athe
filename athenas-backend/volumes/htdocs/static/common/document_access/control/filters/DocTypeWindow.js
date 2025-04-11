Ext._define('common.document_access.control.filters.DocTypeWindow', {
    extend: 'common.document_access.control.filters.BaseWindow',

    getDocTypeField: function (cfg) {
        if (!this._docTypeField) {
            this._docTypeField = Ext._create('core.fields.AutocompleteField', {
                name: 'document_type',
                rest: 'common.document_access.documenttype.Restful',
                fieldLabel: 'Tipo de documento',
                anchor: '99%',
                allowBlank: false,
                gridConfig: {
                    allowCreate: false,
                    allowUpdate: false,
                    allowRemove: false,
                    columnAction: false,
                    configOrderToolBar: ['search', '->', 'download'],
                }
            });
        }

        return this._docTypeField;
    },

    getFormFields: function (cfg) {
        return [ this.getDocTypeField(cfg) ];
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        common.document_access.control.filters.DocTypeWindow.superclass.constructor.call(this, cfg);
    }
});
