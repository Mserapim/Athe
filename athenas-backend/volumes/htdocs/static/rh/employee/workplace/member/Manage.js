/**
 *
 **/

Ext._define('rh.employee.workplace.member.Manage', {
    extend: 'rh.employee.workplace.Manage',

    getGrid: function() {
        if(!this._grid)
            this._grid = Ext._create('rh.employee.workplace.member.Grid', {
                region: 'center',
                border: false,
            });

        return this._grid;
    },

    constructor: function(cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
               title: 'Gestor de Lotação de Membro'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: this.getGrid()
            }
        );

        rh.employee.workplace.member.Manage.superclass.constructor.call(this, cfg);
    }
});
