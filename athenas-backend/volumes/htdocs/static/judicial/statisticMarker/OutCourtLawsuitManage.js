
function _super(me) {
    return me.supr()
}

Ext._define('judicial.statisticMarker.OutCourtLawsuitManage', {
    'extend': 'Ext.Window',

    width: 1100,
    height: 680,

    getCommandPanel: function(cfg) {
        if (!this._commandPanel) {
            this._commandPanel = Ext._create('Ext.Panel', {
                width: 65,
                frame: true,
                layout: {
                    type: 'vbox',
                    align: 'center',
                    pack: 'center',
                    defaultMargins: '4px 0'
                },
                items: [
                    {
                        tooltip: 'Adicionar todos visiveis',
                        iconCls: 'icon-core icon-core-add-all',
                        xtype: 'button',
                        width: 36,
                        height: 36,
                        scope: this,
                        handler: function () { this.addAllItems() }
                    },
                    {
                        tooltip: 'Adicionar selecionado',
                        iconCls: 'icon-core icon-core-add-selected',
                        xtype: 'button',
                        width: 36,
                        height: 36,
                        scope: this,
                        handler: function() { this.addSelectedItem() }
                    },
                    {
                        tooltip: 'Remover selecionado',
                        iconCls: 'icon-core icon-core-remove-selected',
                        xtype: 'button',
                        width: 36,
                        height: 36,
                        scope: this,
                        handler: function() { this.removeSelectedItem() }
                    },
                    {
                        tooltip: 'Remover todos visiveis',
                        iconCls: 'icon-core icon-core-remove-all',
                        xtype: 'button',
                        width: 36,
                        height: 36,
                        scope: this,
                        handler: function () { this.removeAllItems() }
                    },
                ]
            });
        }

        return this._commandPanel;
    },

    removeSelectedItem: function() {
        this.removeItem(
            this.getSelectedGrid().getSelectionModel().getSelections()
        );
    },

    removeAllItems: function () {
        var selected = [];

        this.getSelectedGrid().getStore().each(function (record) { selected.push(record); });
        this.removeItem(selected);
    },

    removeItem: function (selections) {
        var lawsuit = Ext._create('judicial.OutCourtLawsuitRestful');
        var me = this;

        if (selections.length > 0) {
            var items = selections.map(function (row) { return row.get('pk') });

            this.selected.forEach(
                function (pk) {
                    lawsuit.relatedRemove(
                        'statistic_markers',
                        pk,
                        items,
                        null,
                        null,
                        {
                            scope: me,
                            fn: function () {
                                this.getAvaliableGrid().getStore().reload();
                                this.getSelectedGrid().getStore().reload();
                            }
                        }
                    );
                });
        } else {
            Ext.Msg.show({
                title: 'Removendo',
                msg: 'Nenhum item foi selecionado para ser removido.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    addSelectedItem: function() {
        this.addItem(
            this.getAvaliableGrid().getSelectionModel().getSelections()
        );
    },

    addAllItems: function() {
        var selected = [];

        this.getAvaliableGrid().getStore().each(function (record) { selected.push(record); });
        this.addItem(selected);
    },

    addItem: function (selections) {
        var lawsuit = Ext._create('judicial.OutCourtLawsuitRestful');
        var me = this;

        if (selections.length > 0) {
            var items = selections.map(function (row) { return row.get('pk') });

            this.selected.forEach(
                function (pk) {
                    lawsuit.relatedAdd(
                        'statistic_markers',
                        pk,
                        items,
                        null,
                        null,
                        {
                            scope: me,
                            fn: function() {
                                this.getAvaliableGrid().getStore().reload();
                                this.getSelectedGrid().getStore().reload();
                            }
                        }
                    );
                });
        } else {
            Ext.Msg.show({
                title: 'Adicionado',
                msg: 'Nenhum item foi selecionado para ser adicionado.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getAvaliableGrid: function(cfg) {
        if (!this._avaliableGrid) {
            var me = this;

            this._avaliableGrid = Ext._create('judicial.statisticMarker.Grid', {
                title: 'Disponíveis',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
                doubleClickHandler: function () {
                    me.addSelectedItem();
                },
                flex: 1,
                configOrderToolBar: ['-', 'search'],
                gridAutoLoad: false
            });

            this._avaliableGrid.setFilterProperty('lawsuits__in', cfg.selected, -100);
        }

        return this._avaliableGrid;
    },

    getSelectedGrid: function(cfg) {
        if (!this._selectedGrid) {
            var me = this;
            this._selectedGrid = Ext._create('judicial.statisticMarker.Grid', {
                title: 'Selecionados',
                columnAction: false,
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false,
                doubleClickHandler: function () {
                    me.removeSelectedItem();
                },
                flex: 1,
                configOrderToolBar: ['-', 'search'],
                gridAutoLoad: false
            });

            this._selectedGrid.setFilterProperty('lawsuits__in', cfg.selected, 100);
        }

        return this._selectedGrid;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.apply(
            cfg,
            {
                title: 'Marcadores estatisticos do procedimento',
                modal: true,
                border: false,
                buttons: [
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: function() { this.close() }
                    }
                ],
                layout: {
                    type: 'hbox',
                    align: 'stretch'
                },
                items: [
                    this.getAvaliableGrid(cfg),
                    this.getCommandPanel(cfg),
                    this.getSelectedGrid(cfg)
                ]
            }
        );

        judicial.statisticMarker.OutCourtLawsuitManage.superclass.constructor.call(this, cfg);
    }
});
