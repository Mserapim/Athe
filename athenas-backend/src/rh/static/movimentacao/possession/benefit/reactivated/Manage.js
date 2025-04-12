
Ext._define('rh.movimentacao.possession.benefit.reactivated.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.movimentacao.possession.benefit.reactivated.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Reativação de Benefício'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.movimentacao.possession.benefit.reactivated.Manage.superclass.constructor.call(this, cfg);
    }
});
