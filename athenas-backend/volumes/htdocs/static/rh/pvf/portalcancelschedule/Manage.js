Ext._define('rh.pvf.portalcancelschedule.Manage', {
    extend: 'toolkit.widget.TabPanel',

    Grid: function() {
        if(!this._grid) {
            this._grid = Ext._create('rh.pvf.portalcancelschedule.Grid', {
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
                    this.Grid(),
                ]
            }
        );

        rh.pvf.portalcancelschedule.Manage.superclass.constructor.call(this, cfg);
    }
});
