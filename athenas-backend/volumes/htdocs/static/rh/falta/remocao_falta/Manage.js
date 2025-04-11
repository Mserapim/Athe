/**
 *
 **/
Ext._define('rh.falta.remocao_falta.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid) {
            this._Grid = Ext._create('rh.falta.remocao_falta.Grid', {
                region: 'center',
                gridAutoLoad: false,
            });

        }

        return this._Grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Faltas'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid()
                ]
            }
        );

        rh.falta.remocao_falta.Manage.superclass.constructor.call(this, cfg);
    }
});
