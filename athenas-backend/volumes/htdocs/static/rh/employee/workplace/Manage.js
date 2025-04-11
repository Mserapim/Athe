/**
 *
 **/

Ext._define('rh.employee.workplace.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.employee.workplace.Grid', {
                region: 'center',
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Lotação do Servidor'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.employee.workplace.Manage.superclass.constructor.call(this, cfg);
    }
});
