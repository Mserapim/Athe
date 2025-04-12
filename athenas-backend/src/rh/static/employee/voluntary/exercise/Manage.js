/**
 *
 **/
Ext._define('rh.employee.voluntary.exercise.Manage', {
	extend: 'rh.employee.workplace.managerbyemployee.Manage',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Voluntário - Lotações e Designações',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.employee.voluntary.exercise.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.employee.voluntary.exercise.Manage.superclass.constructor.call(this, cfg);
	}
});
