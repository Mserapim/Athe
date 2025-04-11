/**
 *
 **/
Ext._define('common.siatu.terceirizada.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.terceirizada.Restful',

    // width: 400,

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 60,
                items: [
                    {
                        xtype: 'textfield',
                        name: 'nome',
                        fieldLabel: 'Nome',
                        allowBlank: false,
                        width: 250,
                    },
                    {
                        xtype: 'textfield',
                        name: 'cnpj',
                        fieldLabel: 'Cnpj',
                        allowBlank: false,
                        width: 250,
                    },
                ]
            });

        return this._formPanel;
    }
});
