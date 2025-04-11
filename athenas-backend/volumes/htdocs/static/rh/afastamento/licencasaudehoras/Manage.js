/**
 *
 **/

Ext._define('rh.afastamento.licencasaudehoras.Manage', {
    extend: 'rh.afastamento.licencasaude.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencasaudehoras.Grid', {
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
               title: 'Gestor de Licença de Saúde de até 3 Dias'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencasaudehoras.Manage.superclass.constructor.call(this, cfg);
    }
});
