/**
 *
 **/
 Ext._define('rh.employee.workplace.workassignmentsubstitution.ManageLimited', {
    extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Exercícios',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    Ext._create('rh.employee.workplace.workassignmentsubstitution.ManagePanel', {
                        region: 'center',
                        departament: cfg.departament
                    })
                ]
            }
        );
        rh.employee.workplace.workassignmentsubstitution.ManageLimited.superclass.constructor.call(this, cfg);
    }
});