 Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.PayrollManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.paycheckdifference.difference_payroll.difference.PayrollGrid', {
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
				items: this.getGrid()
			}
		);

		rh.gfp.paycheckdifference.difference_payroll.difference.PayrollManage.superclass.constructor.call(this, cfg);
	}
});
