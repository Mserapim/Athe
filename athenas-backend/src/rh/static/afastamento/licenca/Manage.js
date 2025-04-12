/**
 *
 **/

Ext._define('rh.afastamento.licenca.Manage', {
    extend: 'rh.afastamento.baselicencaafastamento.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licenca.Grid', {
                region: 'center',
                hideItemsToolbar: ['remove'],
                hideActions: ['remove'],
                allowRemove: false
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Licença'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licenca.Manage.superclass.constructor.call(this, cfg);
    }
});
