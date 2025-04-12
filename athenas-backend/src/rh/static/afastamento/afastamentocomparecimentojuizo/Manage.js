/**
 *
 **/

Ext._define('rh.afastamento.afastamentocomparecimentojuizo.Manage', {
    extend: 'rh.afastamento.afastamento.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.afastamentocomparecimentojuizo.Grid', {
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
               title: 'Gestor de Afastamento por Comparecimento em Juízo'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.afastamentocomparecimentojuizo.Manage.superclass.constructor.call(this, cfg);
    }
});
