
Ext._define('rh.afastamento.council.Manage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
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
                items: Ext._create('rh.afastamento.council.ManagerTab', {
                    department: cfg.department,
                    region: 'center'
                })
            }
        );

        rh.afastamento.council.Manage.superclass.constructor.call(this, cfg);
    }
});
