/**
 *
 **/
Ext._define('rh.ferias.configuration.message.Panel', {
    extend: 'core.RestfulPanel',


    rest: 'rh.ferias.configuration.message.Restful',

    _prepareSuccessCallback: function(callback) {
        var wnd = this;
        var success = callback.success;

        function foo(args) {
            core.invokeCallback(
                success,
                args
            );
        };

        callback.success = {
            'fn': foo
        };

        return callback
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'label',
                        text: 'Escolha as opções de forma de envio de notificações. Por padrão, as notificações aparecem no mensageiro no menu do servidor.',
                        style: 'font-size: 14px;',
                    },
                    {height:10},
                    {
                        xtype:'fieldset',
                        title: 'Tipo de decisão',
                        autoHeight:true,
                        items:[
                        {
                            xtype: 'checkbox',
                            name: 'servidor_tipo_deferimento',
                            boxLabel: 'Servidor - Deferimento',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'membro_tipo_deferimento',
                            boxLabel: 'Membro - Deferimento',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'servidor_tipo_indeferimento',
                            boxLabel: 'Servidor - Indeferimento',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'membro_tipo_indeferimento',
                            boxLabel: 'Membro - Indeferimento',
                            hideLabel: true,
                            allowBlank: true,
                        }]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Tipo de Notificação',
                        autoHeight:true,
                        items:[
                        {
                            xtype: 'checkbox',
                            name: 'servidor_notificacao_destaque',
                            boxLabel: 'Servidor - Apresentar notificação em Destaque',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'membro_notificacao_destaque',
                            boxLabel: 'Membro -  Apresentar notificação em Destaque',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'servidor_notificacao_email_institucional',
                            boxLabel: 'Servidor - Enviar notificação através de email institucional',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'membro_notificacao_email_institucional',
                            boxLabel: 'Membro - Enviar notificação através de email institucional',
                            hideLabel: true,
                            allowBlank: true,
                        }
                        ]
                    },
                    {
                        xtype: 'button',
                        text: 'Salvar',
                        width: 100,
                        height: 25,
                        scope: this,
                        handler: this.save,
                    }
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                labelWidth:150,
                labelAlign:'right',
                action: 'update',
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                        }
                    }
                }
            }
        );

        Ext.apply(
            cfg,
            {

            }
        );

        rh.ferias.configuration.message.Panel.superclass.constructor.call(this, cfg);
    }
})