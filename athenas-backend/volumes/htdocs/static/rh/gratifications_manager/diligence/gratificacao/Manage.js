Ext._define('rh.gratifications_manager.diligence.gratificacao.Manage', {
	extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gratificação de Designação para Diligência'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
			}
		);

		rh.gratifications_manager.diligence.gratificacao.Manage.superclass.constructor.call(this, cfg);
	}
});