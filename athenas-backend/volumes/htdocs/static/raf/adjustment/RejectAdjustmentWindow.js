Ext._define('raf.adjustment.RejectAdjustmentWindow', {
    extend: 'Ext.Window',

    reject: function() {
        var rest = Ext._create('raf.adjustment.AdjustmentInternalControlRestful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Rejeitar pedido de ajuste...'});
        var values = this.getFormPanel().getForm().getValues();

        values.adjustment_list = (this.values.adjustment_list || 0);
        
        mask.show();
        rest.action(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();

                        Ext.Msg.show({
                            title: 'Rejeitar pedido de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Rejeitar pedido de ajuste',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Rejeitar pedido de ajuste',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype: "hidden",
                        name: "situation",
                    },
                    {
                        xtype:'fieldset',
                        title: 'Parecer',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                           {
                               fieldLabel: "Resposta",
                               xtype: "ckeditor",
                               hideLabel: true,
                               allowBlank: false,
                               name: "answer",
                               submit: true,
                               height: 600,
                           }
                        ]
                    },
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Rejeitar pedido de ajuste',
        });

        Ext.apply(cfg, {
            width: 900,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Indeferir pedido',
                    scope: this,
                    handler: function() { this.reject(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });


        raf.adjustment.RejectAdjustmentWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(this.values !== undefined ? this.values : {});
    }
});
