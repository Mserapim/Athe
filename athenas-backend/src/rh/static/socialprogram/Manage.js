/**
 *
 **/

Ext._define('rh.socialprogram.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.socialprogram.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Programa Social'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.socialprogram.Manage.superclass.constructor.call(this, cfg);
    }
});
