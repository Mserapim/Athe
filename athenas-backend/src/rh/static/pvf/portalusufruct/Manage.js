Ext._define('rh.pvf.portalusufruct.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getUsufructGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('rh.pvf.portalusufruct.Grid', {
                region: 'center',
                gridAutoLoad: false
                
            });
        }

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Usufrutos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getUsufructGrid(),
                ]
            }
        );

        rh.pvf.portalusufruct.Manage.superclass.constructor.call(this, cfg);
    }
});
