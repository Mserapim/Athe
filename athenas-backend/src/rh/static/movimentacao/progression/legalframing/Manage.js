
Ext._define('rh.movimentacao.progression.legalframing.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {     
        if(!this._grid)
            this._grid = Ext._create('rh.movimentacao.progression.legalframing.Grid', {
                region: 'center'
            });
        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Movimentação de Enquadramento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.movimentacao.progression.legalframing.Manage.superclass.constructor.call(this, cfg);
    }
});
