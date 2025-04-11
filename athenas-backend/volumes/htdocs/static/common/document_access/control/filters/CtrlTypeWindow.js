Ext._define('common.document_access.control.filters.CtrlTypeWindow', {
    extend: 'common.document_access.control.filters.BaseWindow',

    getCtrlTypeField: function (cfg) {
        if (!this._ctrlTypeField) {
            this._ctrlTypeField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Nível de acesso',
                allowBlank: false,
                displayField: 'title',
                rest: 'common.document_access.controltype.Restful',
                anchor: '99%'
            });
        }

        return this._ctrlTypeField;
    },

    getFormFields: function (cfg) {
        return [ this.getCtrlTypeField(cfg) ];
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        common.document_access.control.filters.CtrlTypeWindow.superclass.constructor.call(this, cfg);
    }
});
