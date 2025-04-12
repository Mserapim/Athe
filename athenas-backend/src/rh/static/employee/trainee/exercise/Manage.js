/**
 *
 **/
Ext._define('rh.employee.trainee.exercise.Manage', {
	extend: 'rh.employee.workplace.managerbyemployee.Manage',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Estagiario - Lotações e Designações',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.employee.trainee.exercise.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.employee.trainee.exercise.Manage.superclass.constructor.call(this, cfg);
	}
});
