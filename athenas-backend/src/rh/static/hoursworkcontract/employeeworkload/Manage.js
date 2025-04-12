/**
 *
 **/
Ext._define('rh.hoursworkcontract.employeeworkload.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getWorkloadGrid: function() {
        if(!this._cworkloadGrid) {
            this._cworkloadGrid = Ext._create('rh.hoursworkcontract.employeeworkload.Grid', {
                region: 'center',
            });
        }

        return this._cworkloadGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Horários e Servidores'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getWorkloadGrid(),
                ]
            }
        );

        rh.hoursworkcontract.employeeworkload.Manage.superclass.constructor.call(this, cfg);
    }
});
