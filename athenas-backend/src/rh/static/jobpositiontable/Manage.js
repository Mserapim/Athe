/**
 *
 **/

Ext._define('rh.jobpositiontable.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function () {
        if (!this._grid) {
            cfg = {
                region: 'center',
            };
            this._grid = Ext._create('rh.jobpositiontable.Grid', cfg);
        }
        return this._grid;
    },

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Cargos em Quadro'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.jobpositiontable.Manage.superclass.constructor.call(this, cfg);
    }
});
