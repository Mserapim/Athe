Ext._define('rh.pvf.portalusufructretification.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getUsufructGrid: function() {
        if(!this._grid) {
            this._grid = Ext._create('rh.pvf.portalusufructretification.Grid', {
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

        rh.pvf.portalusufructretification.Manage.superclass.constructor.call(this, cfg);
    }
});
