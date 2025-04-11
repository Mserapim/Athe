/**
 *
 **/

Ext._define('rh.afastamento.licencasaudejuntamedica.Manage', {
    extend: 'rh.afastamento.licencasaude.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.afastamento.licencasaudejuntamedica.Grid', {
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
               title: 'Gestor de Licença Saúde Junta Médica'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.afastamento.licencasaudejuntamedica.Manage.superclass.constructor.call(this, cfg);
    }
});
