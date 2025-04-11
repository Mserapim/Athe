/**
 *
 **/

Ext._define('rh.afastamento.ausenciadoacaosangue.Manage', {
    extend: 'rh.afastamento.ausencia.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.ausenciadoacaosangue.Grid', {
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
               title: 'Gestor de Ausência por Doação de Sangue'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.ausenciadoacaosangue.Manage.superclass.constructor.call(this, cfg);
    }
});
