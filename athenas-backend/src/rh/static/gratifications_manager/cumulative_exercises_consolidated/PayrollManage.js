 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.PayrollManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gratifications_manager.cumulative_exercises_consolidated.PayrollGrid', {
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

		rh.gratifications_manager.cumulative_exercises_consolidated.PayrollManage.superclass.constructor.call(this, cfg);
	}
});
