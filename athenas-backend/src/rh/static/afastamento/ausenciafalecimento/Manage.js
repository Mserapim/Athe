/**
 *
 **/

Ext._define('rh.afastamento.ausenciafalecimento.Manage', {
    extend: 'rh.afastamento.ausencia.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.ausenciafalecimento.Grid', {
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
               title: 'Gestor de Ausência por Falecimento'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.ausenciafalecimento.Manage.superclass.constructor.call(this, cfg);
    }
});
