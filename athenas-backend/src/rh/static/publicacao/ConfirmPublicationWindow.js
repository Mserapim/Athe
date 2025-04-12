
Ext._define('rh.publicacao.ConfirmPublicationWindow', {
    extend: 'Ext.Window',

    title: 'Confirmar para publicação',

    width: 550,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 150,
                items: [
                    {
                        fieldLabel: 'Identificação',
                        xtype: 'displayfield',
                        name: 'unicode',
                        submitValue: false
                    },
                    {
                        fieldLabel: 'Veículo',
                        xtype: 'displayfield',
                        name: 'veiculo_publicacao_display',
                        submitValue: false
                    },
                    {
                        fieldLabel: 'Número da publicação',
                        xtype: 'numberfield',
                        name: 'numero_publicacao',
                    },
                    {
                        fieldLabel: 'Data da publicação',
                        xtype: 'datefield',
                        name: 'data_publicacao',
                    },
                    {
                        fieldLabel: 'Página',
                        xtype: 'numberfield',
                        name: 'vehicle_page',
                    },
                ]
            });

        return this._formPanel;
    },

    sentTo: function() {
        var rest = Ext._create('rh.publicacao.Restful');
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo informações...'});

        mask.show();
        rest.confirmPublication(
            this.oId,
            values,
            {
                scope: this,
                fn: function() {
                    this.grid.getStore().reload();
                    this.close();
                }
            },
            {
                scope: this,
                fn: function(msg) {
                    Ext.Msg.show({
                        title: 'Enviando para publicação',
                        msg: msg,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                fn: function() {
                    mask.hide();
                    mask = undefined;
                }
            }
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Enviar',
                    scope: this,
                    handler: this.sentTo
                },
                {
                    text: 'Cancelar',
                    scope: this,
                    handler: this.close
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                items: [
                    this.getFormPanel(cfg)
                ],
                buttons: this.getButtons(cfg)
            }
        );

        rh.publicacao.ConfirmPublicationWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues(cfg.values || {});
    }
});
