
Ext._define('rh.movimentacao.fired.terminationbenefit.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.movimentacao.fired.terminationbenefit.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Desligamento do Benefício'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.movimentacao.fired.terminationbenefit.Manage.superclass.constructor.call(this, cfg);
    }
});
