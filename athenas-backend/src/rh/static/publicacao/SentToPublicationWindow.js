
Ext._define('rh.publicacao.SentToPublicationWindow', {
    extend: 'Ext.Window',

    title: 'Enviar para publicação',

    width: 450,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                items: [
                    {
                        fieldLabel: 'Identificação',
                        xtype: 'displayfield',
                        name: 'unicode',
                        submitValue: false
                    },
                    {
                        xtype: 'choicefield',
                        fieldLabel: 'Veículo',
                        hiddenName: 'veiculo_publicacao',
                        width: 315,
                        allowBlank: true,
                        choiceId: 'rh.VEICULO_PUBLICACAO'
                    }
                ]
            });

        return this._formPanel;
    },

    sentTo: function() {
        var rest = Ext._create('rh.publicacao.Restful');
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Persistindo informações...'});

        mask.show();
        rest.sentToPublication(
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

        rh.publicacao.SentToPublicationWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues(cfg.values || {});
    }
});
