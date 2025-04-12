Ext._define('cif.attachment.AttachmentWindow', {
    extend: 'core.RestfulWindow',

    rest: 'cif.attachment.AttachmentRestful',

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
                        fieldLabel: "Título",
                        name: "title",
                        xtype: "textfield",
                        width: 665
                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Anexo",
                        xtype: "ged-fileuploadfield",
                        name: "attach",
                        width: 665
                    },

                ]
            });

        return this._formPanel;
    }
});
