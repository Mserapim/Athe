Ext._define('core.dashboard.EmployeePortalPanel', {
    extend: 'Ext.Panel',

    getXTemplate: function (cfg) {
        if (this._template) {
            return this._template;
        }

        this._template = Ext._create('Ext.XTemplate', [
            '<div class="intranet intranet-menu">',
                '<ul>',
                    '<tpl for=".">',
                        '<li><a href="{href}" target="{target}">{text}</a></li>',
                    '</tpl>',
                '</ul>',
            '</div>',
        ]);

        return this._template;
    },

    getStore: function () {
        if (this._store) {
            return this._store;
        }

        this._store = Ext._create('Ext.data.JsonStore', {
            fields: ['text', 'href', 'target'],
            url: toolkit.util.action('intranet/get_menu/json'),
            root: 'list',
            totalProperty: 'total',
            autoLoad: true,
            remoteSort: true,
            baseParams: {start: 0, limit: 20},
        });

        return this._store;
    },

    getDataView: function (cfg) {
        if (this._dataView) {
            return this._dataView;
        }

        this._dataView = Ext._create('Ext.DataView', {
            store: this.getStore(cfg),
            itemSelector: '.list-item',
            emptyText: 'Sem itens para exibir.',
            tpl: this.getXTemplate(cfg),
        });

        return this._dataView;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            //title: 'Portal do servidor',
        });

        Ext.apply(cfg, {
            autoScroll: true,
            items: [
                this.getDataView(cfg),
            ],
        });

        core.dashboard
          .EmployeePortalPanel
          .superclass
          .constructor
          .call(this, cfg);
    },
});
