
Ext._define('rh.afastamento.baselicencaafastamento.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.baselicencaafastamento.Grid', {
                region: 'center'
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Base - Licença Aafastamento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.baselicencaafastamento.Manage.superclass.constructor.call(this, cfg);
    }
});
