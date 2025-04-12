/**
 *
 **/

Ext._define('rh.gfp.parameters.RRAEmployeePayrollTypeManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.parameters.RRAEmployeePayrollTypeGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'RRA Servidor (Restful)'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.parameters.RRAEmployeePayrollTypeManage.superclass.constructor.call(this, cfg);
	}
});
