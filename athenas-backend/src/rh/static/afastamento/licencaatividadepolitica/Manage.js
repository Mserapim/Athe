/**
 *
 **/

Ext._define('rh.afastamento.licencaatividadepolitica.Manage', {
    extend: 'rh.afastamento.licenca.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencaatividadepolitica.Grid', {
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
               title: 'Gestor de Licença para Atividade Política'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencaatividadepolitica.Manage.superclass.constructor.call(this, cfg);
    }
});
