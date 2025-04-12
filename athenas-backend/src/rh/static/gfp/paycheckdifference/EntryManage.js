/**
 *
 **/

Ext._define('rh.gfp.paycheckdifference.EntryManage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.gfp.paycheckdifference.EntryGrid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Lançamentos com difereças'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.gfp.paycheckdifference.EntryManage.superclass.constructor.call(this, cfg);
    }
});
