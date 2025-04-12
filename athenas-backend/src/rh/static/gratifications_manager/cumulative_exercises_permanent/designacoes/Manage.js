Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Grid', {
				region: 'center',
			});
		}

		return this._grid;
	},

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Designações'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		rh.gratifications_manager.cumulative_exercises_permanent.designacoes.Manage.superclass.constructor.call(this, cfg);
	}
});