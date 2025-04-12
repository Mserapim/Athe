
Ext._define('planning.hiring.minutesolicitationmanager.EdocTextWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minutesolicitationmanager.MinuteSolicitationManagerRestful',

    width: 640,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                layout: 'fit',
                items: [
                    {
                        width: 870,
                        height: 420,
                        allowBlank: true,
                        name: "textoedoc",
                        xtype: "ckeditor",
                    },
                ]
            });

        return this._formPanel;
    },

    insertText: function(msg) {
        this.getFormPanel().getForm().findField('textoedoc').setValue(msg);
    },

    toRequisit: function(id) {
        var rest = Ext._create('planning.hiring.minutesolicitationrequisition.MinuteSolicitationRequisitionRestful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Alterando situação...' });

        mask.show();
        rest.toRequisit(
            id,
            {
                scope:this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Mensagem',
                        msg: "Situação alterada",
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope:this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Erro',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    mask.hide();
                }
            },
            {
                scope:this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() {
                        this.close();
                    }
                },
                {
                    text: 'Gravar Pedido',
                    scope: this,
                    handler: function() {
                        Ext.Msg.show({
                            title: 'Gerando pedido',
                            msg: 'A situação do pedido será alterada para "Solicitado". Deseja continuar?',
                            icon: Ext.Msg.QUESTION,
                            buttons: Ext.Msg.YESNO,
                            scope: this,
                            fn: function(btn) {
                                if (btn === 'no') return;
                
                                this.toRequisit(this.oId);
                            }
                        });
                    }
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Pedido',
            width: 900,
            height: 600,
        });

        Ext.apply(cfg, {
            items: this.getFormPanel(),
        });

        planning.hiring.minutesolicitationmanager.EdocTextWindow.superclass.constructor.call(this, cfg);
    },
});
