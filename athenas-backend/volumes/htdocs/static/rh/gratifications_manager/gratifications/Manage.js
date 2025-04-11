/**
 *
 **/
Ext._define('rh.gratifications_manager.gratifications.Manage', {
	extend: 'toolkit.widget.TabPanel',

	constructor: function(cfg) {
		cfg = core.nullValue(cfg, {});
		Ext.applyIf(
			cfg,
			{
                title: 'Conferência de Gratificações',
                layout: 'border',
                scope: this,
                items:  Ext._create('rh.gratifications_manager.gratifications.ManagePanel', {departament: cfg.departament})
            }
        );
		rh.gratifications_manager.gratifications.Manage.superclass.constructor.call(this, cfg);
	}
});
