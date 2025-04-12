/**
 *
 **/

Ext._define('rh.afastamento.folgaeleitoral.Manage', {
    extend: 'rh.afastamento.baselicencaafastamento.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.folgaeleitoral.Grid', {
                region: 'center',
                // hideItemsToolbar: ['remove'],
                // hideActions: ['remove'],
                allowRemove: false
            });
        }
        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Folga eleitoral'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.folgaeleitoral.Manage.superclass.constructor.call(this, cfg);
    }
});
