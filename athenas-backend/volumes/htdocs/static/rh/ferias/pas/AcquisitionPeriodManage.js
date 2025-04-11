/**
 *
 **/

Ext._define('rh.ferias.pas.AcquisitionPeriodManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.ferias.pas.AcquisitionPeriodGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Período Aquisitivo'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.ferias.pas.AcquisitionPeriodManage.superclass.constructor.call(this, cfg);
	}
});
