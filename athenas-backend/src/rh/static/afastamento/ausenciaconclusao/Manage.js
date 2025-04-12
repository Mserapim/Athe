/**
 *
 **/

Ext._define('rh.afastamento.ausenciaconclusao.Manage', {
    extend: 'rh.afastamento.ausencia.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.ausenciaconclusao.Grid', {
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
               title: 'Gestor de Ausência por Conclusão'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.ausenciaconclusao.Manage.superclass.constructor.call(this, cfg);
    }
});
