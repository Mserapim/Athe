Ext._define('esocial.configuration.ConfigurationCertificateWindow', {
    extend: 'Ext.Window',

    width: 400,
    height: 250,

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        title: 'Informações do Certificado',
                        xtype: 'fieldset',
                        items: [
                            {
                                xtype: "ged-fileuploadfield",
                                fieldLabel: "Certificado Digital A1(pfx, p12)",
                                allowBlank: true,
                                rest: "ged.arquivo.ArquivoRestful",
                                name: "certificate"
                            },
                            {
                                xtype: 'textfield',
                                name: 'certificate_passwd',
                                inputType: 'password',
                                fieldLabel: 'Senha do Certificado Digital',
                                allowBlank: true,
                                width: 160
                            },
                            {
                                xtype: "ged-fileuploadfield",
                                fieldLabel: "Certificado Digital CAs",
                                allowBlank: true,
                                rest: "ged.arquivo.ArquivoRestful",
                                name: "certificate_ca"
                            },
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    save: function (close) {
        var form = this.getFormPanel().getForm();

        try {
            form.submit({
                url: toolkit.util.Normalize.controller_action('ESOCIALConfiguration', 'update_certificate'),
                scope: this,
                success: function (form, action) {
                    this.success && this.success.callback.call(this.success.scope ? this.success.scope : window);
                    if (close) this.destroy();
                    Ext.Msg.show({
                        title: 'Atualização de certificado',
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK,
                        msg: action.result.message
                    });
                },
                failure: function (form, action) {
                    Ext.Msg.show({
                        title: 'Atualização de certificado',
                        icon: Ext.Msg.WARNING,
                        buttons: Ext.Msg.OK,
                        msg: action.result.message,
                    })
                },
                scope: this,
                waitMsg: 'Salvado configurações...'
            });
        } catch (e) {
            console.debug(e);
        }
    },

    constructor: function (cfg) {
        cfg = (cfg ? cfg : {});

        Ext.apply(
            cfg,
            {
                title: 'Atualização do Certificado',
                modal: true,
                resizable: false,
                border: false,
                items: this.getFormPanel(),
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: function () { this.save(true) }
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        esocial.configuration.ConfigurationCertificateWindow.superclass.constructor.call(this, cfg);
    }
});

