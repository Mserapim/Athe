Ext._define('planning.hiring.minutesolicitationpayment.MinuteSolicitationPaymentExecutionWindow', {
    extend: 'Ext.Window',

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
                        name: 'bank_order'
                    },
                    {
                        xtype: 'datefield',
                        name: 'payment_date',
                        fieldLabel: 'Data do Pagamento',
                    },
                ]
            });

        return this._formPanel;
    },

    pay: function() {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Lançando Pagamento...'});
        mask.show();
        Ext.Ajax.request({
            url: core.callAction('PHMMinuteSolicitationPayment', 'pay'),
            scope: this,
            params: {
                pk: this.params.payment,
                bank_order: values.bank_order,
                payment_date: values.payment_date
            },
            success: function(response, options) {
                var obj = Ext.decode(response.responseText);
                if (obj.success)
                    this.params.paymentGrid.getStore().reload();

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

        planning.hiring.minutesolicitationpayment.MinuteSolicitationPaymentExecutionWindow.superclass.constructor.call(this, cfg);
    }
});
