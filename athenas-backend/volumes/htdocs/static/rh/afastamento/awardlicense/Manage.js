/**
 *
 **/

Ext._define('rh.afastamento.awardlicense.Manage', {
    extend: 'rh.afastamento.licenca.Manage',

    getGrid: function () {
        if (!this._grid)
            this._grid = Ext._create('rh.afastamento.awardlicense.Grid', {
                region: 'center',
                allowRemove: false
            });

        return this._grid;
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Licença de Prêmio'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.awardlicense.Manage.superclass.constructor.call(this, cfg);
    }
});
