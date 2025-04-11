var storeCache = {};

Ext._define('corregedoria.cirdir.HistoryWindow', {
    extend: 'core.RestfulWindow',

    getHistoryGrid: function(cfg) {
        if(!this._historyGrid)
            this._historyGrid = Ext._create('corregedoria.cirdir.history.Grid', {
                layout: 'form',
                border: true,
                height: 425,
                gridAutoLoad: false,
                columnAction: false,
                configOrderToolBar: ['search', ],
                hideItemsToolbar:['add', 'edit', 'remove','download', '-'],
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
                doubleClickHandler: function(grid) { },
           });
        return this._historyGrid;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getHistoryGrid(cfg)
                ]
            });
        return this._formPanel;
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
                }
            ];

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Histórico',
            width: 1300,
            height: 500,
            modal: true,
        });
        Ext.apply(cfg, {
            items: this.getFormPanel(cfg),
        });
        corregedoria.cirdir.HistoryWindow.superclass.constructor.call(this, cfg);
        this.getHistoryGrid().addFilterProperty('controlinformation_id', cfg.params.controlinformation, 100, false);
        this.getHistoryGrid().addFilterProperty('criteria', cfg.params.criteria_key, 101, true);
    }
});
