Ext._define('rh.employee.specialized.Manage', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Servidor',
                layout: 'border',
                border: false,
                region: 'center',
                scope: this,
                items:  Ext._create('rh.employee.specialized.tab.Manage', {
                    departament: cfg.departament,
                    organIdentifier: cfg.organIdentifier,
                    matriculaFieldBlocked: cfg.matriculaFieldBlocked
                })
            }
        );
        rh.employee.specialized.Manage.superclass.constructor.call(this, cfg);
    }
});
