 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getPeriodoExercCumulPermGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Grid', {
				region: 'center',
				gridAutoLoad: true,
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
				doubleClickHandler: function(grid) { },
			});
		}

		return this._eventGrid;
	},

	getExercCumulConsolidadoGrid: function(cfg) {
		if(!this._exerc_cumul_perm)
			this._exerc_cumul_perm = Ext._create('rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Grid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				flex: 0.5,
				height: 550,
				hideColumns:[],
                viewConfig: {
                    stripeRows: false,
				},
			});

		return this._exerc_cumul_perm;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Exercícios Cumulativos Permanentes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
				},
				items:[
					this.getExercCumulConsolidadoGrid(cfg),
				]
			}
		);

		rh.gratifications_manager.cumulative_exercises_permanent.consolidado.Manage.superclass.constructor.call(this, cfg);
	}
});
