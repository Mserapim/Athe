
Ext._define('rh.socialprogram.Window', {
    extend: 'core.RestfulWindow',

    rest: 'rh.socialprogram.Restful',

    width: 450,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                {
                    width: 310,
                    maxLength: 200,
                    allowBlank: false,
                    fieldLabel: "Nome",
                    name: "name",
                    xtype: "textfield"
                }
            ]
            });

        return this._formPanel;
    }
});

