/**
 *
 **/

Ext._define('rh.gfp.payroll.BankingEmployeeTypePayrollManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.payroll.BankingEmployeeTypePayrollGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Dados bancários por tipo de folha'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.payroll.BankingEmployeeTypePayrollManage.superclass.constructor.call(this, cfg);
	}
});
