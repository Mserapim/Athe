Ext._define('nomeacao.cadastramento.Window', {
    extend: 'core.RestfulWindow',

    rest: 'nomeacao.cadastramento.Restful',

    width: 650,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "textfield", 
                        fieldLabel: "CPF", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "cpf",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Nome", 
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "nome",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Nome Social",
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "nome_social",
                    },
                    {
                        xtype: "textfield", 
                        fieldLabel: "Sincronizado em",
                        allowBlank: true,
                        disabled: true,
                        width: 500,
                        name: "created_at",
                    },
                    // {
                    //     allowBlank: true,
                    //     fieldLabel: 'Sincronizar?',
                    //     name: 'sinc_form',
                    //     xtype: 'checkbox'
                    // },
                ]
            });

        return this._formPanel;
    }
});
