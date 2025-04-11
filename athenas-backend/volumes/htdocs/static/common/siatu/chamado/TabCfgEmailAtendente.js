/**
 *
 **/
Ext._define('common.siatu.chamado.TabCfgEmailAtendente', {
    extend: 'core.RestfulPanel',

    rest: 'common.siatu.chamado.Restful',

    setChamado: function(pk) {
        this.oId = pk;
    },

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

    getButtons: function() {},

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                flex: 1.0,
                border: false,
                labelWidth:90,
                labelAlign:'right',
                items: [
                    {
                        xtype: 'label',
                        text: 'Marque as opções de mudança de estado que deseja receber notificação para o chamado selecionado',
                        style: 'font-size: 14px;',
                    },
                    {height:10},
                    {
                        xtype: 'checkbox',
                        name: 'atendente_transferido_atendente',
                        boxLabel: 'Transferido Atendente',
                        allowBlank: true,
                    },
                    {
                        xtype: 'checkbox',
                        name: 'atendente_apos_avaliacao',
                        boxLabel: 'Após Avaliação',
                        allowBlank: true,
                    },
                    {
                        layout: 'table',
                        layoutConfig:{
                            columns: 2,
                        },
                        items:[
                            {
                                width: 90,
                                height: 100,
                            },
                            {
                                align: 'bottom',
                                xtype: 'button',
                                text: 'Salvar',
                                width: 100,
                                height: 25,
                                scope: this,
                                handler: this.save,
                            }
                        ]
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                action: 'update',
                params:{cfg_email_atendente:1}
            }
        );

        Ext.apply(
            cfg,
            {
                title:'Notificação',
                layout: 'hbox',
                layoutConfig:{
                    align: 'stretch',
                },
            }
        );

        common.siatu.chamado.TabCfgEmailAtendente.superclass.constructor.call(this, cfg);
    }

});
