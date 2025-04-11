/**
 *
 **/
 Ext._define('rh.employee.workplace.managerbyworkplace.Manage', {
    extend: 'rh.employee.workplace.managerbyemployee.Manage',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Local - Lotações e Designações',
                layout: 'border',
                border: false,
                scope: this,
                items:  Ext._create('rh.employee.workplace.managerbyworkplace.ManagePanel', {})
            }
        );
        rh.employee.workplace.managerbyworkplace.Manage.superclass.constructor.call(this, cfg);
    }
});

