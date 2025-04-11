Ext._define('common.document_access.legalprerogative.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getLegalPrerogativeGrid: function() {
        if (!this._grid) {
            this._grid = Ext._create('common.document_access.legalprerogative.Grid', {
                region: 'center',
                gridAutoLoad: true,
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Gestor de Hipótese Legal'
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: this.getLegalPrerogativeGrid(),
        });

        common.document_access.legalprerogative.Manage.superclass.constructor.call(this, cfg);
    }
});
