/**
 *
 **/

Ext._define('rh.afastamento.ausenciaeleitor.Manage', {
    extend: 'rh.afastamento.ausencia.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.ausenciaeleitor.Grid', {
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
               title: 'Gestor de Ausência por Eleitoral'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.ausenciaeleitor.Manage.superclass.constructor.call(this, cfg);
    }
});
