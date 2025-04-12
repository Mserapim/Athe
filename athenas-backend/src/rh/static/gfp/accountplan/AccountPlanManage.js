/**
 *
 **/

Ext._define('rh.gfp.accountplan.AccountPlanManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.accountplan.AccountPlanGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Plano de Contas (Restful)'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.accountplan.AccountPlanManage.superclass.constructor.call(this, cfg);
	}
});
