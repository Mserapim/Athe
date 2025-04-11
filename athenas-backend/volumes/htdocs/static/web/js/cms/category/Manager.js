Ext._define('web.cms.category.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function(cfg)
    {
        if(!this._grid)
        {
            this._grid = Ext._create('web.cms.category.Grid', {
                region: 'center',
                gridAutoLoad: false,
            });

            var filter = [];

            if(cfg.state && cfg.state.site_pk)
            {
                filter.push({
                    property: 'sites',
                    value: cfg.state.site_pk,
                    stage: 1000,
                })
            }

            if(this.category_id)
                filter.push({
                    property: 'parent',
                    value: this.category_id,
                    stage: 2000
                });

            this._grid.setFilter(filter);
        }

        return this._grid;
    },

    constructor: function(cfg)
    {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Categorias',
            layout: 'border',
            items: [this.getGrid(cfg)]
        });

        sessionStorage.setItem("cms-state", JSON.stringify(cfg.state || {}));

        web.cms.category.Manager.superclass.constructor.call(this, cfg);
    }
});