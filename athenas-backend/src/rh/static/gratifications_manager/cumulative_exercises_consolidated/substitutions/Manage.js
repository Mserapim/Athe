 Ext._define('rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Manage', {
	extend: 'toolkit.widget.TabPanel',

	event: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
	},

	getCumulativeExercisesGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Grid', {
				region: 'center',
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

		constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Substituições'
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
					this.getCumulativeExercisesGrid(cfg),
				]
			}
		);

		rh.gratifications_manager.cumulative_exercises_consolidated.substitutions.Manage.superclass.constructor.call(this, cfg);
	}
});
