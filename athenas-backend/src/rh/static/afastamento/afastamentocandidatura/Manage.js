/**
 *
 **/

Ext._define('rh.afastamento.afastamentocandidatura.Manage', {
    extend: 'rh.afastamento.afastamento.Manage',

    getGrid: function() {
        if(!this._grid){
            this._grid = Ext._create('rh.afastamento.afastamentocandidatura.Grid', {
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
               title: 'Gestor de Afastamento de Candidatura'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.afastamentocandidatura.Manage.superclass.constructor.call(this, cfg);
    }
});
