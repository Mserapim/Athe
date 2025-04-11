
Ext._define('rh.afastamento.ManagerEmployee', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Afastamentos do Servidor'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid({
                        department: cfg.department
                    }),
                ]
            }
        );

        rh.afastamento.ManagerEmployee.superclass.constructor.call(this, cfg);
    },

    getGrid: function (args) {
        if (!this._grid)
            this._grid = Ext._create('rh.afastamento.ManagerEmployeeGrid', {
                department: args.department,
                region: 'center'
            });

        return this._grid;
    },
});
