/**
 *
 **/
Ext._define('common.siatu.terceiro.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.terceiro.Restful',

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
                        name: 'cpf',
                        fieldLabel: 'cpf',
                        allowBlank: false,
                        width: 250,
                    },
                    {
                        xtype: 'textfield',
                        name: 'telefone',
                        fieldLabel: 'Telefone',
                        allowBlank: false,
                        width: 250,
                    },
                    {
                        xtype: 'textarea',
                        name: 'endereco',
                        fieldLabel: 'Endereço',
                        allowBlank: false,
                        width: 250,
                    },
                ]
            });

        return this._formPanel;
    }
});
