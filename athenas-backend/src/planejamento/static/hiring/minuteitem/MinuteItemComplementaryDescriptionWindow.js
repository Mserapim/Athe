Ext._define('planning.hiring.minuteitem.MinuteItemComplementaryDescriptionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minuteitem.MinuteItemComplementaryDescriptionRestful',
    width: 440,

    getFormPanel: function() {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        fieldLabel: "Característica",
                        xtype: "textfield",
                        name: "characteristic",
                        allowBlank: false,
                        maxLength: 128,
                        width: 300
                    },
                    {
                        fieldLabel: "Descrição",
                        xtype: "textfield",
                        name: "description",
                        allowBlank: false,
                        maxLength: 128,
                        width: 300
                    }
                ]
            });

        return this._formPanel;
    }
});
