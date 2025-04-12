Ext._define('raf.yearbase.Window', {
    extend: 'core.RestfulWindow',

    rest: 'raf.yearbase.Restful',

    width: 500,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        width: 360,
                        allowBlank: false,
                        fieldLabel: "Ano Base",
                        name: "title",
                        xtype: "textfield"
                    },
                    {
                        allowBlank: false,
                        fieldLabel: "Vigência",
                        name: "valid_of",
                        xtype: "datefield"
                    },
                    {
                        xtype: "checkbox",
                        boxLabel: "Ativo",
                        fieldLabel: "",
                        allowBlank: true,
                        name: "activated"
                    }
                ]
            });

        return this._formPanel;
    }
});
