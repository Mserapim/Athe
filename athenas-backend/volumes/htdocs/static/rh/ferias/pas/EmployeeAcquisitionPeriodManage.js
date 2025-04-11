/**
 *
 **/

Ext._define('rh.ferias.pas.EmployeeAcquisitionPeriodManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.ferias.pas.EmployeeAcquisitionPeriodGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Período Aquisitivo Servidor'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.ferias.pas.EmployeeAcquisitionPeriodManage.superclass.constructor.call(this, cfg);
	}
});
