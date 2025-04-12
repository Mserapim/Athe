Ext._define('corregedoria.inspection.attachment.AttachmentWindow', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.attachment.AttachmentRestful',

    width: 800,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        maxLength: 100,
                        allowBlank: false,
                        fieldLabel: "Descrição",
                        name: "description",
                        xtype: "textfield",
                        width: 665
                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Anexo",
                        xtype: "ged-fileuploadfield",
                        name: "attached_file",
                        width: 665
                    },

                ]
            });

        return this._formPanel;
    }
});
