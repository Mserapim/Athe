/**
 * OBS: A instanciação dessa classe depende de uma configuração de banco de dados:
 *
 * Menu de Aplicativos
 *  |
 *  +-> PAINEL DE CONTROLE
 *       |
 *       +-> Eventos para o usuário
 *            |
 *            +-> Item no grid: "Associação Usuário/Servidor"
 **/
Ext._define('auth.LinkUserServidorWindow', {
    'extend': 'Ext.Window',

    'getFormPanel': function() {
        if(!this._formPanel)
            this._formPanel = new Ext.form.FormPanel({
                'border': false,
                'frame': true,
                'labelWidth': 135,
                'items': [
                    {
                        'fieldLabel': 'Sua matricula',
                        'xtype': 'textfield',
                        'name': 'matricula',
                        'allowBlank': false
                    },
                    {
                        'fieldLabel': 'Seu CPF',
                        'xtype': 'cpffield',
                        'name': 'cpf',
                        'allowBlank': false
                    },
                    {
                        'fieldLabel': 'Data de Nascimento',
                        'xtype': 'datefield',
                        'name': 'nascimento',
                        'allowBlank': false
                    },
                ]
            });

        return this._formPanel;
    },

    'submit': function() {
        var form = this.getFormPanel().getForm();

        form.waitMsgTarget = this.getEl();

        form.submit({
            'url': core.callAction('ExtLogin', 'first_access'),
            'method': 'POST',
            'waitMsg': 'Processando informações...',
            'scope': this,
            'success': function(form, action) {
                location.reload();
                this.destroy();
            },
            'failure': function(form, action) {
                var message = '';

                if(action.failureType == 'server')
                    message = action.result.msg;
                else
                    message = 'Ocorreu um erro de comunicação com servidor, tente novamente mais tarde.';

                Ext.Msg.show({
                    'title': 'Validando dados',
                    'icon': Ext.Msg.ERROR,
                    'buttons': Ext.Msg.OK,
                    'msg': message
                });
            }
        });
    },

    'constructor': function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                'title': 'Ligar Usuário ao Servidor'
            }
        );

        Ext.apply(
            cfg,
            {
                'border': false,
                'resizable': false,
                'closable': false,
                'width': 330,
                'items': [this.getFormPanel()],
                'buttons': [
                    {
                        'text': 'Validar',
                        'scope': this,
                        'handler': this.submit
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        auth.LinkUserServidorWindow.superclass.constructor.call(this, cfg);
    }
});
