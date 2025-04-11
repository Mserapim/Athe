
Ext._define('rh.afastamento.Manager', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function (cfg) {
        cfg = cfg ? cfg : {};

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Afastamentos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: Ext._create('rh.afastamento.ManagerTab', {
                    department: cfg.department,
                    region: 'center'
                })
            }
        );

        rh.afastamento.Manager.superclass.constructor.call(this, cfg);
    }
});
