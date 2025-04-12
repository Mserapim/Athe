/**
 *
 **/

Ext._define('rh.employee.linktoemployee.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.employee.linktoemployee.Grid', {
                region: 'center',
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Vínculo do Servidor'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.employee.linktoemployee.Manage.superclass.constructor.call(this, cfg);
    }
});
