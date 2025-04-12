var storeCache = {};
Ext._define('corregedoria.scoretable.ListBandScoreTableWindow', {
    extend: 'Ext.Window',

    getBandScoreTableGrid: function(cfg) {
        if(!this._scoreTableGrid) {
            this._scoreTableGrid = Ext._create('corregedoria.scoretable.bandscoretable.Grid', {
                region: 'center',
                layout: 'form',
                border: true,
                height: 250,
                width: 880,
                gridAutoLoad: true,
                columnAction: false,
                hideItemsToolbar:['download', '-', 'search'],
                doubleClickHandler: function() { },
                params: {
                    configscoretable: cfg.params.scoretable
                }
            });
            this.getBandScoreTableGrid(cfg).setFilterProperty('configscoretable', cfg.params.scoretable, 100);
        }
        return this._scoreTableGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 375,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'Tabela de Pontuação',
                        collapsible: false,
                        autoHeight:true,
                        width: 880,
                        items:[
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 1,
                                items: [
                                    {
                                        xtype: 'displayfield',
                                        name: 'scoretable_display',
                                        style: {fontWeight: 'bold', },
                                    },
                                ]
                            },
                        ]
                    },
                    this.getBandScoreTableGrid(cfg),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {

        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Faixas para a Tabela de Pontuação',
            width: 910,
            height: 395,
            modal: true,
        });
        Ext.apply(cfg, {
            items: this.getFormPanel(cfg),
            buttons: [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ]
        });
        corregedoria.scoretable.ListBandScoreTableWindow.superclass.constructor.call(this, cfg);
        this.getFormPanel().getForm().setValues({'scoretable_display': cfg.params.scoretable_display});
    }
});
