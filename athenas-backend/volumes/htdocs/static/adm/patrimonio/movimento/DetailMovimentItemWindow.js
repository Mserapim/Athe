
Ext._define('adm.patrimonio.movimento.DetailMovimentItemWindow', {
    extend: 'Ext.Window',

    getTilePagePanel: function(cfg) {
        if(!this._tilePagePanel)
            this._tilePagePanel = Ext._create('core.TilePagePanel', {
                height: 325,
                papperModel: 'card',
                title: 'Descrição'
            });

        return this._tilePagePanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    {
                        xtype: 'panel',
                        frame: true,
                        layout: 'form',
                        items: [
                            {
                                fieldLabel: 'Plaqueta',
                                xtype: 'displayfield',
                                name: 'patrimonio_plaqueta',
                                value: 'Carregando...'
                            },
                            {
                                fieldLabel: 'Especie',
                                xtype: 'displayfield',
                                name: 'patrimonio_unicode',
                                value: 'Carregando...'
                            },
                            {
                                fieldLabel: 'Consevação',
                                xtype: 'displayfield',
                                name: 'patrimonio_conservacao',
                                value: 'Carregando...'
                            }
                        ]
                    },
                    this.getTilePagePanel(cfg)
                ]
            });

        return this._formPanel;
    },

    readData: function() {
        var rest = Ext._create('adm.patrimonio.movimento.ItemRestful');

        rest.get(
            this.pk,
            {
                success: {
                    scope: this,
                    fn: function(instance) {
                        this.getFormPanel().getForm().setValues(instance);
                        this.getTilePagePanel().setPageContent(instance.patrimonio_descricao);
                    }
                }
            },
            {
                el: this.getEl(),
                msg: 'carregando...'
            }
        );
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Visualização de Item de Movimentação',
                modal: true
            }
        );

        Ext.apply(
            cfg,
            {
                border: false,
                width: 700,
                items: [
                    this.getFormPanel(cfg)
                ],
                listeners: {
                    scope: this,
                    render: function() {
                        this.readData();
                    }
                },
                buttons: [
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function() { this.close(); }
                    }
                ]
            }
        );

        adm.patrimonio.movimento.DetailMovimentItemWindow.superclass.constructor.call(this, cfg);
    }
});
