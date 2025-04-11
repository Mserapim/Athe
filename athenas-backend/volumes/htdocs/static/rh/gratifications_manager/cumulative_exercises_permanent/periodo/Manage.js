 Ext._define('rh.gratifications_manager.cumulative_exercises_permanent.periodo.Manage', {
	extend: 'toolkit.widget.TabPanel',

	event: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._event = value;

			if(dispatch) this.observeEvent();
		}
		else
			return this._event;
	},

	observeEvent: function(){
        var selection = this.getPeriodoExercCumulPermGrid().getSelectionModel().getSelections();
		if(this.event() && selection.length == 1){
			this.getExercCumulConsolidadoGrid().enable();
			this.getExercCumulConsolidadoGrid()._event = this.event();
			this.getExercCumulConsolidadoGrid().setParam('periodo', this.event().pk);
			this.getExercCumulConsolidadoGrid().setFilterProperty('periodo', this.event().pk, 100);
		}
		else{
			this.getExercCumulConsolidadoGrid().disable();
			this.getExercCumulConsolidadoGrid().getStore().removeAll();
			this.getExercCumulConsolidadoGrid().setFilterProperty('periodo', 0, 100, false);
		}
    },

	getPeriodoExercCumulPermGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gratifications_manager.cumulative_exercises_permanent.periodo.Grid', {
				region: 'center',
				gridAutoLoad: true,
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
				doubleClickHandler: function(grid) { },
			});

			this._eventGrid.getSelectionModel().on({
				scope: this,
				beforerowselect: function(eventGrid){
					return true
				},
				rowselect: function(eventGrid, index, record){
					this.event(record.data);
				},
				rowdeselect: function(eventGrid, index, record){
					this.event(null);
				},
			});
	
			this._eventGrid.getStore().on({
				scope: this,
				beforeload: function(st, options){
					rec = this._eventGrid.getSelectionModel().getSelected();
					this._eventGrid._lastEvent = rec? rec.data.pk: null;
				},
				load: function(st, records, options){
					if(!records.length)
						this.event(null);
				}
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
					this.getPeriodoExercCumulPermGrid(cfg),
					this.getExercCumulConsolidadoGrid(cfg),
				]
			}
		);

		rh.gratifications_manager.cumulative_exercises_permanent.periodo.Manage.superclass.constructor.call(this, cfg);
	}
});
