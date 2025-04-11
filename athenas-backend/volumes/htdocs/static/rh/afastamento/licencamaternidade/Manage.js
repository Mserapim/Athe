/**
 *
 **/

Ext._define('rh.afastamento.licencamaternidade.Manage', {
    extend: 'rh.afastamento.licencasaudejuntamedica.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencamaternidade.Grid', {
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
               title: 'Gestor de Licença Saúde Doença na Família'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencamaternidade.Manage.superclass.constructor.call(this, cfg);
    }
});
