Ext._define('common.document_access.control.filters.SourceWindow', {
    extend: 'common.document_access.control.filters.BaseWindow',

    getSourceField: function (cfg) {
        if (!this._sourceField) {
            this._sourceField = Ext._create('core.fields.AutocompleteField', {
                name: 'source',
                rest: 'rh.generalorgan.Restful',
                //rest: 'rh.workplace.Restful',
                fieldLabel: 'Origem',
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

        return this._sourceField;
    },

    getFormFields: function (cfg) {
        return [ this.getSourceField(cfg) ];
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        common.document_access.control.filters.SourceWindow.superclass.constructor.call(this, cfg);
    }
});
