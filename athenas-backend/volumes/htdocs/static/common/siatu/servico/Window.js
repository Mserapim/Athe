/**
 *
 **/
Ext._define('common.siatu.servico.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.servico.Restful',
    width: '340',

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 55,
                items: [       
                    {
                        xtype: 'textfield',
                        name: 'nome',
                        fieldLabel: 'Servico',
                        allowBlank: false,
                        width: 240,
                    },
                ]
            });

        return this._formPanel;
    }
});
