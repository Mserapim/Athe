/**
 *
 **/
Ext._define('adm.patrimonio.avaliacao.TabelaCopyWindow', {
    extend: 'Ext.Window',

    width: 550,

    getButtons: function() {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Copiar dados'
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

        return this._buttons;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                border: false,
                items: [
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'De',
                        name: 'src',
                        allowBlank: false,
                        rest: 'adm.patrimonio.avaliacao.TabelaRestful',
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: 'Para',
                        name: 'dst',
                        allowBlank: false,
                        rest: 'adm.patrimonio.avaliacao.TabelaRestful',
                    },
                    {
                        boxLabel: 'Copiar dados de depreciação',
                        xtype: 'checkbox'
                    },
                    {
                        boxLabel: 'Tabela de conceito',
                        xtype: 'checkbox'
                    },
                    {
                        boxLabel: 'Tabela de perído de utilização',
                        xtype: 'checkbox'
                    },
                    {
                        boxLabel: 'Tabela de vida útil futura',
                        xtype: 'checkbox'
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
                title: 'Copiar dados da tabela'
            }
        );

        Ext.apply(
            cfg,
            {
                resizable: false,
                border: false,
                items: this.getFormPanel(),
                buttons: this.getButtons()
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.avaliacao.TabelaCopyWindow.superclass.constructor.call(this, cfg);
    }
});
