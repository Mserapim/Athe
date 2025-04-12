Ext._define('raf.functionalactivityreport.FollowAdjustmentWindow', {
    extend: 'Ext.Window',

    getInGrid: function(cfg) {
        if(!this._inGrid) {
            this._inGrid = Ext._create('raf.adjustment.AdjustmentEmployeeGrid', {
                title: 'Em análise',
                split: true,
                border: false,
                hideItemsToolbar: ['remove', 'download'],
                columnAction: false,
                gridAutoLoad: false,
                allowRemove: false,
                disabled: false,
                colorized: true,
                detailView: this.getTilePanel(),
                storeDefaultRoute: 'inbox_waiting_conversation_employee',
                configOrderToolBar: ['edit'],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                params: {
                    adjustment: 0
                }
            });
            this._inGrid.setFilterProperty('situation__in', [0, 1, 5], 1000, false);
            this._inGrid.setFilterProperty('activity__workerlocation__raf__pk', this.raf(cfg), 1001);
        }
        return this._inGrid;
    },

    getOutGrid: function(cfg) {
        if(!this._outGrid) {
            this._outGrid = Ext._create('raf.adjustment.AdjustmentEmployeeGrid', {
                title: 'Histórico',
                split: true,
                border: false,
                hideItemsToolbar: ['remove', 'download', '-'],
                columnAction: false,
                gridAutoLoad: false,
                allowRemove: false,
                disabled: false,
                detailView: this.getTilePanel(),
                configOrderToolBar: ['-'],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true})
            });
            this._outGrid.setFilterProperty('situation__in', [2, 3, 4, 6], 1000, false);
            this._outGrid.setFilterProperty('activity__workerlocation__raf__pk', this.raf(cfg), 1001);
        }
        return this._outGrid;
    },

    raf: function(cfg) {
        return cfg.params.raf === undefined ? 0 : cfg.params.raf;
    },

    getTilePanel: function(cfg) {
        if(!this._tilePanel)
            this._tilePanel = Ext._create('core.TilePagePanel', {
                region: 'east',
                split: true,
                width: Ext.getBody().getBox().width * 0.6,
                minWidth: Ext.getBody().getBox().width * 0.2,
                maxWidth: Ext.getBody().getBox().width * 0.8
            });
        return this._tilePanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    getBoxPanel: function(cfg) {
        if(!this._boxPanel)
            this._boxPanel = Ext._create('Ext.Panel', {
                region: 'center',
                split: true,
                border: false,
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        height: cfg.height - 65,
                        items: [
                            this.getInGrid(cfg),
                            this.getOutGrid(cfg),
                        ]
                    }
                ]
            });
        return this._boxPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Acompanhar Solicitações de Ajuste',
                modal: true,
                width: Ext.getBody().getBox().width * 0.9,
                height: Ext.getBody().getBox().height * 0.9
            }
        );
        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                buttons: this.getButtons(),
                items: [
                    this.getBoxPanel(cfg),
                    this.getTilePanel(cfg)
                ]
            }
        );
        raf.functionalactivityreport.FollowAdjustmentWindow.superclass.constructor.call(this, cfg);
    }
});
