Ext._define('common.saci.attachment.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.saci.attachment.Restful',

    width: 450,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                defaults: {
                    width: 315
                },
                items: [
                    {
                        maxLength: 100,
                        allowBlank: false,
                        fieldLabel: "Título",
                        name: "title",
                        xtype: "textfield"
                    },
                    {
                        xtype: "ged-fileuploadfield",
                        fieldLabel: "Documento",
                        allowBlank: false,
                        name: "file_descriptor"
                    }
                ]
            });

        return this._formPanel;
    }
});
