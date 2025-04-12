Ext._define('core.dashboard.notification.Panel', {
    extend: 'Ext.Panel',

    getListView: function (cfg) {
        if (this._listView) {
            return this._listView;
        }

        this._listView = Ext._create('core.dashboard.notification.ListView');

        return this._listView;
    },

    getBottomToolbar: function (cfg) {
        if (this._bottomToolbar) {
            return this._bottomToolbar;
        }

        this._bottomToolbar = Ext._create('Ext.PagingToolbar', {
            store: this.getListView(cfg).getStore(),
            displayInfo: true,
            pageSize: 10,
        });

        return this._bottomToolbar;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            //title: 'My Panel',
        });

        Ext.apply(cfg, {
            autoScroll: true,
            items: this.getListView(cfg),
            bbar: this.getBottomToolbar(cfg),
            listeners: {
                scope: this,
                afterrender: function (panel) {
                    this.getListView(cfg).setLoadMaskTarget(panel.getEl());
                },
            }
        });

        core.dashboard
          .notification
          .Panel
          .superclass
          .constructor
          .call(this, cfg);
    },
});
