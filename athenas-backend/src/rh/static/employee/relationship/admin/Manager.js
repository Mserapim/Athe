/**
 *
 **/

Ext._define('rh.employee.relationship.Admin.Manager', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.employee.relationship.Admin.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Relações de confiança (Admin)'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.employee.relationship.Admin.Manager.superclass.constructor.call(this, cfg);
	}
});
