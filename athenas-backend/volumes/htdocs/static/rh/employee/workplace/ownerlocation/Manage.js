/**
 *
 **/

Ext._define('rh.employee.workplace.OwnerLocationManage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.employee.workplace.ownerlocation.Grid', {
                region: 'center',
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Lotação de Membro Owner Location'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.employee.workplace.OwnerLocationManage.superclass.constructor.call(this, cfg);
    }
});
