/**
 *
 **/

Ext._define('rh.afastamento.ausencia.Manage', {
    extend: 'rh.afastamento.baselicencaafastamento.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.ausencia.Grid', {
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
               title: 'Ausência'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.ausencia.Manage.superclass.constructor.call(this, cfg);
    }
});
