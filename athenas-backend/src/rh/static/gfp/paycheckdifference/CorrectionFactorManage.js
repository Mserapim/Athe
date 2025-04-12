/**
 *
 **/

Ext._define('rh.gfp.paycheckdifference.CorrectionFactorManage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.gfp.paycheckdifference.CorrectionFactorGrid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Fatores de correção'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.gfp.paycheckdifference.CorrectionFactorManage.superclass.constructor.call(this, cfg);
    }
});
