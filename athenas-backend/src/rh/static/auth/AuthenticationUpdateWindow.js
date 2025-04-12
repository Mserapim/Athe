
Ext._define('rh.auth.AuthenticationUpdateWindow', {
    extend: 'Ext.Window',

    updateInformation: function() {
        var rest = Ext._create('rh.person.naturalperson.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Atualizando informações...'});

        mask.show();
        rest.doRequest(
            rest.getRoute('update_personal_mail_and_password', false, 'POST', {
                scope: this,
                params: this.getFormPanel().getForm().getValues(),
                callback: function() { mask.hide(); },
                success: function(xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if(!rst.success)
                        Ext.Msg.show({
                            title: 'Atualizando informações',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    else {
                        Ext.Msg.show({
                            title: 'Atualizando informações',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                        this.close();
                    }
                },
                failure: function(xhr) {
                    Ext.Msg.show({
                        title: 'Atualizando informações',
                        msg: 'Recursos indisponivel no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });

                    this.close();
                }
            })
        );
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                labelWidth: 145,
                items: [
                    {
                        fieldLabel: 'Email institucional',
                        xtype: 'textfield',
                        width: 250,
                        name: 'email_institucional'
                    },
                    {
                        fieldLabel: 'Confirmar email institucional',
                        xtype: 'textfield',
                        width: 250,
                        name: 'confirm_email_institucional'
                    },
                    {
                        fieldLabel: 'Senha atual',
                        xtype: 'textfield',
                        inputType: 'password',
                        name: 'password'
                    },
                    {
                        fieldLabel: 'Nova senha',
                        xtype: 'textfield',
                        inputType: 'password',
                        name: 'new_password'
                    },
                    {
                        fieldLabel: 'Confirmar nova senha',
                        xtype: 'textfield',
                        inputType: 'password',
                        name: 'confirm_new_password'
                    }
                ],
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: this.updateInformation
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.apply(cfg, {
            width: 435,
            title: 'Atualização de Email Institucional',
            closable: false,
            items: [
                this.getFormPanel(cfg)
            ]
        });

        rh.auth.AuthenticationUpdateWindow.superclass.constructor.call(this, cfg);
    }
});
