/**
 *
 **/
Ext._define('rh.employee.outsourced.exercise.Manage', {
	extend: 'rh.employee.workplace.managerbyemployee.Manage',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Terceirizado - Lotações e Designações',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.employee.outsourced.exercise.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.employee.outsourced.exercise.Manage.superclass.constructor.call(this, cfg);
	}
});
