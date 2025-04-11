/**
 *
 **/

Ext._define('rh.afastamento.afastamentoeleitoral.Manage', {
    extend: 'rh.afastamento.afastamento.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.afastamentoeleitoral.Grid', {
                region: 'center',
                hideItemsToolbar: ['remove'],
                hideActions: ['remove'],
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
               title: 'Gestor de Afastamento Eleitoral'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.afastamentoeleitoral.Manage.superclass.constructor.call(this, cfg);
    }
});
