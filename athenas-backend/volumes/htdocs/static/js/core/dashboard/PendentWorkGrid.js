Ext._define('core.dashboard.PendentWorkGrid', {
    extend: 'Ext.grid.GridPanel',

    _doubleClickEvent: function(event) {
        var selected = this.getSelectionModel().getSelected();

        if (selected && selected.get('controller')) {
            toolkit.Application.createFormFor(selected.get('controller'));
        }
    },

    _afterRenderEvent: function(grid) {
        if (this.gridAutoLoad) {
            this.getStore().load({});
        }
    },

    getStore: function (cfg) {
        if (this._store) {
            return this._store;
        }

        this._store = Ext._create('Ext.data.JsonStore', {
            url: core.callAction('UtilWaitingWorkController', 'store'),
            root: 'collection',
            totalProperty: 'count',
            fields: [
                {name: 'keyId', type: 'string'},
                {name: 'title', type: 'string'},
                {name: 'type', type: 'string'},
                {name: 'count', type: 'int'},
                {name: 'controller', type: 'string'},
            ],
        });

        return this._store;
    },

    rendererCount: function(value, cell, record) {
        return '<div style="text-align:left">' + value + ' ' + record.get('type') + '</div>';
    },

    getBottomToolbar: function (cfg) {
        if (this._bottomToolbar) {
            return this._bottomToolbar;
        }

        this._bottomToolbar = Ext._create('Ext.PagingToolbar', {
            store: this.getStore(),
            autoScroll: true,
            displayInfo: true,
        });

        return this._bottomToolbar;
    },

    getColumnModel: function(cfg) {
        if (this._columnModel) {
            return this._columnModel;
        }

        this._columnModel = Ext._create('Ext.grid.ColumnModel', [
            new Ext.grid.RowNumberer(),
            { header: 'Trabalhos', dataIndex: 'title', id: 'autoExpandColumn', },
            { header: 'Total', dataIndex: 'count', width: 100 , renderer: this.rendererCount, },
        ]);

        return this._columnModel;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            gridAutoLoad: true,
            stripeRows: true,
            loadMask: true,
        });

        Ext.apply(cfg, {
            store: this.getStore(),
            autoExpandColumn: 'autoExpandColumn',
            colModel: this.getColumnModel(cfg),
            bbar: this.getBottomToolbar(cfg),
            listeners: {
                scope: this,
                dblclick: this._doubleClickEvent,
                afterrender: this._afterRenderEvent,
            }
        });

        core.dashboard
          .PendentWorkGrid
          .superclass
          .constructor
          .call(this, cfg);
    },
});
