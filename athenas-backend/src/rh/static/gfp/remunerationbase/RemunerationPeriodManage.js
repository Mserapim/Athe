/**
 *
 **/

Ext._define('rh.gfp.remunerationbase.RemunerationPeriodManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.remunerationbase.RemunerationPeriodGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Cache de Remunerações'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.remunerationbase.RemunerationPeriodManage.superclass.constructor.call(this, cfg);
	}
});
