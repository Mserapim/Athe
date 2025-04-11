Ext._define('common.distribution.player.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.distribution.player.Restful',

    width: 500,

    getFormPanel: function (cfg) {
        if (!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 50,
                labelAlign: 'right',
                items: [
                    {
                        xtype: 'textfield',
                        fieldLabel: 'Título',
                        name: 'title',
                        maxLength: 100,
                        anchor: '99%',
                        allowBlank: false
                    },
                    {
                        xtype: 'checkbox',
                        fieldLabel: 'Ativo',
                        name: 'active',
                        checked: true,
                        allowBlank: false
                    }
                ]
            });
        }
        
        return this._formPanel;
    }
});
