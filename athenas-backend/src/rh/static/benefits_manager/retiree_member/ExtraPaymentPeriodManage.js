Ext._define('rh.benefits_manager.retiree_member.ExtraPaymentPeriodManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('rh.benefits_manager.retiree_member.ExtraPaymentPeriodGrid', {
				region: 'center',
				params: {extra_payment: cfg.extra_payment},
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Membros Aposentados'
			}
		);

		console.log('Manage')

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);

		rh.benefits_manager.retiree_member.ExtraPaymentPeriodManage.superclass.constructor.call(this, cfg);
	}
});
