Ext._define('rh.gratifications_manager.aux_coordenation.gratificacao.Manage', {
	extend: 'toolkit.widget.TabPanel',

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gratificação de Auxiliar Coordenação'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
			}
		);

		rh.gratifications_manager.aux_coordenation.gratificacao.Manage.superclass.constructor.call(this, cfg);
	}
});