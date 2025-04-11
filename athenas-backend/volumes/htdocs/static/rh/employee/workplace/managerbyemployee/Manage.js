/**
 *
 **/
Ext._define('rh.employee.workplace.managerbyemployee.Manage', {
	extend: 'toolkit.widget.TabPanel',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Servidor - Lotações e Designações',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.employee.workplace.managerbyemployee.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.employee.workplace.managerbyemployee.Manage.superclass.constructor.call(this, cfg);
	}
});
