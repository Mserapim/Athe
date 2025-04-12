/**
 *
 **/
Ext._define('rh.employee.apprentice.exercise.Manage', {
	extend: 'rh.employee.workplace.managerbyemployee.Manage',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Jovem Cidadão - Aprendiz',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.employee.apprentice.exercise.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.employee.apprentice.exercise.Manage.superclass.constructor.call(this, cfg);
	}
});
