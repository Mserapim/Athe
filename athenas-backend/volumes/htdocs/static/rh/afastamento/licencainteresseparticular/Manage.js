/**
 *
 **/

Ext._define('rh.afastamento.licencainteresseparticular.Manage', {
    extend: 'rh.afastamento.licenca.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencainteresseparticular.Grid', {
                region: 'center',
                // hideItemsToolbar: ['remove'],
                // hideActions: ['remove'],
                allowRemove: false
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Licença Interesse Particular'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencainteresseparticular.Manage.superclass.constructor.call(this, cfg);
    }
});
