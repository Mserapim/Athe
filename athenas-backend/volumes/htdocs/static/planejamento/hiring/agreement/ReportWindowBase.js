Ext._define('planning.hiring.agreement.ReportWindowBase', {
    extend: 'Ext.Window',

    width: 435,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 100,
                autoHeight: true,
                items: this._getDocumentsFields(cfg)
            });

        return this._formPanel;
    },

    _getDocumentsFields: function(cfg) {
        return [
            {
                allowBlank: true,
                fieldLabel: "Contratado",
                name: "pessoa",
                xtype: "rest-autocompletefield",
                rest: "rh.pessoa.Restful"
            },
            {
                layout: 'column',
                items: [
                    {
                        columnWidth: '0.5',
                        layout: 'form',
                        items:
                            {
                                width: 200,
                                allowBlank: false,
                                fieldLabel: 'Início',
                                name: 'data_inicio',
                                xtype: 'datefield',
                            }
                    },
                    {
                        columnWidth: '0.5',
                        layout: 'form',
                        items:
                            {
                                width: 200,
                                allowBlank: false,
                                fieldLabel: 'Fim',
                                name: 'data_vencimento',
                                xtype: 'datefield',
                            }
                    }
                ]
            }
        ];
    },

    generate: function() { /* sobrescrever */ },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                resizable: false,
                border: false
            }
        );

        Ext.apply(
            cfg,
            {
                items: [
                    this.getFormPanel(),
                ],
                buttons: [
                    {
                        text: 'Gerar',
                        scope: this,
                        handler: function() { this.generate(false); }
                    },
                    {
                        text: 'Gerar e novo',
                        scope: this,
                        handler: function() { this.generate(true); }
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );
        planning.hiring.agreement.ReportWindowBase.superclass.constructor.call(this, cfg);
    }
});
