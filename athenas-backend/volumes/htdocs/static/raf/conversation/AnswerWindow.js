Ext._define('raf.conversation.AnswerWindow', {
    extend: 'Ext.Window',


    communication: function() {
        var rest = Ext._create('raf.conversation.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Comunicação...'});
        var values = this.getFormPanel().getForm().getValues();

        values.conversation = (this.values.conversation || 0);
        values.origin = (this.values.origin || 0);
        values.situation = (this.values.situation || 0);

        mask.show();
        rest.conversation(
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                        this.close();
                        Ext.Msg.show({
                            title: 'Comunicação',
                            msg: rst.message,
                            icon: Ext.Msg.INFO,
                            buttons: Ext.Msg.OK
                        });
                    }
                    else
                        Ext.Msg.show({
                            title: 'Comunicação',
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
                        title: 'Comunicação',
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
                        fieldLabel: "Solicitação",
                        xtype: "ckeditor",
                        hideLabel: true,
                        allowBlank: false,
                        name: "message",
                        submit: true,
                        height: 600,
                    }
                ]
            });

        return this._formPanel;
    },


    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Comunicação',
        });

        Ext.apply(cfg, {
            width: 900,
            items: [
                this.getFormPanel(cfg)
            ],
            buttons: [
                {
                    text: 'Enviar',
                    scope: this,
                    handler: function() { this.communication(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });


        raf.conversation.AnswerWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(this.values !== undefined ? this.values : {});
    }
});
