Ext._define('web.cms.metadata.MetaValueManager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function()
    {
        if(!this._grid)
        {
            this._grid = Ext._create('web.cms.metadata.MetaValueGrid', {
                // region: 'center',
                gridAutoLoad: false,
                site: this.site
            });

            var filter = [
                {
                    property: 'active',
                    value: 'on',
                    stage: 1
                }
            ];

            if(this.site)
            {
                filter.push({
                    property: 'key__site',
                    value: this.site,
                    stage: 2
                });
            }

            this._grid.setFilter(filter);
        }

        return this._grid;
    },

    constructor: function(cfg)
    {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Metadados',
            layout: 'fit'
        });

        web.cms.metadata.MetaValueManager.superclass.constructor.call(this, cfg);
        this.add(this.getGrid());
        this.doLayout();
    }
});