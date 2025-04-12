
Ext._define('common.saci.typology.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.saci.typology.Restful',

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
                        fieldLabel: "Tipologia",
                        name: "name",
                        xtype: "textfield"
                    }
                ]
            });

        return this._formPanel;
    }
});

