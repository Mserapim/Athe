/**
 *
 **/

Ext._define('rh.afastamento.licencasaude30dias.Manage', {
    extend: 'rh.afastamento.licencasaude.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencasaude30dias.Grid', {
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
               title: 'Gestor de Licença de Saúde de até 30 Dias'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencasaude30dias.Manage.superclass.constructor.call(this, cfg);
    }
});
