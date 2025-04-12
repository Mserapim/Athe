/**
 *
 **/
Ext._define('common.siatu.configuration.email.Panel', {
    extend: 'core.RestfulPanel',


    rest: 'common.siatu.configuration.email.Restful',

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
            fn: foo
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
                        text: 'Marque as opções de mudança de estado que deseja atribuir como configuração padrão de notificações para os próximos chamados',
                        style: 'font-size: 14px;',
                    },
                    {height:10},
                    {
                        xtype:'fieldset',
                        title: 'Solicitante',
                        autoHeight:true,
                        items:[
                        {
                            xtype: 'checkbox',
                            name: 'solicitante_aguardando_avaliacao',
                            boxLabel: 'Aguardando avaliação',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'solicitante_transferido_atendente',
                            boxLabel: 'Transferido Atendente',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'solicitante_garantia',
                            boxLabel: 'Garantia',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'solicitante_terceirizada',
                            boxLabel: 'Terceirizada',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'solicitante_viagem',
                            boxLabel: 'Viagem',
                            hideLabel: true,
                            allowBlank: true,
                        }]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Atendente',
                        autoHeight:true,
                        items:[
                        {
                            xtype: 'checkbox',
                            name: 'atendente_transferido_atendente',
                            boxLabel: 'Transferido Atendente',
                            hideLabel: true,
                            allowBlank: true,
                        },
                        {
                            xtype: 'checkbox',
                            name: 'atendente_apos_avaliacao',
                            boxLabel: 'Após Avaliação',
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

        common.siatu.configuration.email.Panel.superclass.constructor.call(this, cfg);
    }
})
