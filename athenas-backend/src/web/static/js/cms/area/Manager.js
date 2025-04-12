Ext._define('web.cms.area.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function()
    {
        if(!this._grid)
        {
            this._grid = Ext._create('web.cms.area.Grid', {
                region: 'center',
                gridAutoLoad: false,
            });

            var filter = [
                {
                    property: 'active',
                    value: 'on',
                    stage: 1
                }
            ];

            if(this.site_id)
                filter.push({
                    property: 'parent',
                    value: this.site_id,
                    stage: 2
                });

            this._grid.setFilter(filter);
        }

        return this._grid;
    },

    constructor: function(cfg)
    {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Áreas',
            layout: 'border',
            items: [this.getGrid()]
        });

        web.cms.area.Manager.superclass.constructor.call(this, cfg);
    }
});