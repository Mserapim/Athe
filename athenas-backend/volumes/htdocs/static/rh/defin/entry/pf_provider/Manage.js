/**
 *
 **/

 Ext._define('rh.defin.entry.pf_provider.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.defin.entry.pf_provider.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Lançamentos - Prestadores PF'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.defin.entry.pf_provider.Manage.superclass.constructor.call(this, cfg);
    }
});
