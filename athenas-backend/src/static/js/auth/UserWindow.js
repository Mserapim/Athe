/**
 *
 **/
Ext._define('auth.UserWindow', {
    'extend': 'core.RestfulWindow',

    'rest': 'auth.UserRestful',

    'width': 435,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        fieldLabel: 'Primeiro Nome',
                        xtype: 'textfield',
                        name: 'first_name',
                    },
                    {
                        fieldLabel: 'Sobrenome',
                        xtype: 'textfield',
                        name: 'last_name',
                    },
                    {
                        fieldLabel: 'Email',
                        xtype: 'textfield',
                        name: 'email',
                    },
                    {
                        boxLabel: 'Ativo',
                        xtype: 'checkbox',
                        name: 'is_active',
                        fieldLabel: ''
                    },
                    {
                        boxLabel: 'Membro da Equipe',
                        xtype: 'checkbox',
                        name: 'is_staff',
                        fieldLabel: ''
                    },
                    {
                        boxLabel: 'Administrador do Sistema',
                        xtype: 'checkbox',
                        name: 'is_superuser',
                        fieldLabel: ''
                    }
                ]
            });

        return this._formPanel;
    }
});

