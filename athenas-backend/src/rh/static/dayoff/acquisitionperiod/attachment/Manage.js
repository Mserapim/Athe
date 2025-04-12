/**
 *
 **/

Ext._define('rh.dayoff.acquisitionperiod.attachment.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.dayoff.acquisitionperiod.attachment.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Anexos*'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.dayoff.acquisitionperiod.attachment.Manage.superclass.constructor.call(this, cfg);
	}
});
