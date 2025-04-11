Ext._define('planning.hiring.meterage.PaymentWindow', {
    extend: 'Ext.Window',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Lançar Pagamento'
        });

        Ext.apply(cfg, {
            width: 400,
            items: [
                this.getFormPanel()
            ],
            buttons: [{
                    text: 'Pagar',
                    scope: this,
                    handler: function() {
                        this.pay();
                        this.close();
                    }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });

        planning.hiring.meterage.PaymentWindow.superclass.constructor.call(this, cfg);
    },

    pay: function() {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Lançando Pagamento...'});
        mask.show();
        Ext.Ajax.request({
            url: core.callAction('PHAMeterage', 'pay'),
            scope: this,
            params: {
                pk: this.params.pagamento,
                ordem_bancaria: values.ordem_bancaria,
                data_pagamento: values.data_pagamento
            },
            success: function(response, options) {
                var obj = Ext.decode(response.responseText);
                if (obj.success)
                    this.params.meterageGrid.getStore().reload();

                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.INFO,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
            },
            failure: function(response, options) {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: response.status
                });
            },
            callback: function(options, success, response) {
                mask.hide();
                mask = null;
            },
        });
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = new Ext.form.FormPanel({
                frame: true,
                labelAlign: 'top',
                items: [{
                        fieldLabel: 'Número da Ordem Bancária',
                        xtype: 'textfield',
                        allowBlank: false,
                        width: '350',
                        name: 'ordem_bancaria'
                    },
                    {
                        xtype: 'datefield',
                        name: 'data_pagamento',
                        fieldLabel: 'Data do Pagamento',
                    },
                ]
            });

        return this._formPanel;
    },
});
