 Ext._define('rh.gfp.gcpp.payroll.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.gcpp.payroll.Grid', {
				region: 'center',
				title: 'Folha de Pagamento'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Folha de Pagamento'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(),
			}
		);

		rh.gfp.gcpp.payroll.Manage.superclass.constructor.call(this, cfg);
	},
});
