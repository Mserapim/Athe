
Ext._define('rh.movimentacao.concession.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.movimentacao.concession.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Movimentação Concessão'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.movimentacao.concession.Manage.superclass.constructor.call(this, cfg);
    }
});
