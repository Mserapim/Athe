Ext._define('judicial.requestexternalaccess.JustificationWindow', {
    extend: 'Ext.Window',

    width: 800,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                layout: 'form',
                items: [
                    {
                        allowBlank: false,
                        fieldLabel: "Relato",
                        name: "justification",
                        xtype: "ckeditor",
                        hideLabel: true,
                        height: 240,
                        submit: true,
                    }
                ]
            });

        return this._formPanel;
    },

    finalize: function() {
        var rest = Ext._create('judicial.requestexternalaccess.Restful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Processando...'});
        var values = this.getFormPanel().getForm().getValues();

        mask.show();
        Ext.Ajax.request({
            url: core.callAction('EJudRequestExternalAccess', 'deny'),
            params: {
                pk: this.oId,
                justification: values.justification
            },
            scope: this,
            callback: function() {
                mask.hide();
                this.close();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    core.invokeCallback((this.callback || {}).success);
                }
                else
                    Ext.Msg.show({
                        title: 'Processando',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Processando',
                    msg: 'Recurso indisponível no momento.',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            }
        });

    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Finalizar',
                    scope: this,
                    handler: function() { this.finalize(); }
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Justificativa'
        });

        Ext.apply(cfg, {
            width: 800,
            items: [
                this.getFormPanel()
            ],
            buttons: [
                this.getButtons(cfg)
            ]
        });

        judicial.requestexternalaccess.JustificationWindow.superclass.constructor.call(this, cfg);
    }
});
