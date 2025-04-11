Ext._define('edocs.protocolo.AttachmentWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.protocolo.AttachmentRestful',

    width: 800,

    getAttachmentField: function (cfg) {
        if (!this._attachmentField) {
            this._attachmentField = Ext._create('core.fields.FileUploadField', {
                fieldLabel: "Anexo",
                allowBlank: false,
                name: "attach",
                value: cfg.values.attach,
                loadingOwner: this,
                width: 715,
                access: core.fields.FileUploadField.ACCESS.PUBLIC,
                listeners: {
                    scope: this,
                    afterchange: function(input, instance) {
                        this.getTitleField().setValue(instance.file_path.split('/')[1]);
                        this.getTitleField().focus();
                    }
                }
            });
        }
        return this._attachmentField;
    },

    getTitleField: function (cfg) {
        if (!this._titleField) {
            this._titleField = Ext._create('Ext.form.TextField', {
                fieldLabel: "Título",
                name: "title",
                allowBlank: false,
                maxLength: 260,
                selectOnFocus: true,
                anchor: '99%',
            });
        }
        return this._titleField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 50,
                items: [
                    this.getAttachmentField(cfg),
                    this.getTitleField(cfg),
                ]
            });
        }
        return this._formPanel;
    }
});
