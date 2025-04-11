/**
 *
 **/
Ext._define('rh.hoursworkcontract.workload.manager.ManageTab', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(
            cfg,
            {
                title: 'Gestor de Escalas e Servidores',
                layout: 'border',
                items: [
                    Ext._create('Ext.TabPanel', {
                        region: 'center',
                        activeTab: 0,
                        items:[
                            Ext._create('rh.hoursworkcontract.workload.manager.Manage', {title: 'Escalas'}),
                            Ext._create('rh.hoursworkcontract.employeeworkload.Grid', {title: 'Servidores e Escalas'})
                        ]
                    })
                ]
            }
        );

        rh.hoursworkcontract.workload.manager.ManageTab.superclass.constructor.call(this, cfg);
    }
});
