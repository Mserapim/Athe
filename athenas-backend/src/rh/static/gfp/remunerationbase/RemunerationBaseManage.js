/**
 *
 **/

Ext._define('rh.gfp.remunerationbase.RemunerationBaseManage', {
	extend: 'toolkit.widget.TabPanel',

	remuneration: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._remuneration = value;

			if(dispatch) this.observeRemuneration();
		}
		else
			return this._remuneration;
	},

	observeRemuneration: function() {
		if(this.remuneration()){
			this.getPeriodGrid().enable();
			this.getPeriodGrid().setParam('remuneration', this.remuneration());
			this.getPeriodGrid().setFilterProperty('remuneration_id', this.remuneration(), 100);
		}
		else{
			this.getPeriodGrid().disable();
			this.getPeriodGrid().getStore().removeAll();
			this.getPeriodGrid().setFilterProperty('remuneration_id', 0, 100, false);
		}
	},

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.remunerationbase.RemunerationBaseGrid', {
				region: 'center',
 				// width: 600,
 	            // minWidth: 600,
				// split: true,
			});
			
			this._grid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.remuneration(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.remuneration(null);
				},
			});

			this._grid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					var rec = this._grid.getSelectionModel().getSelected();
					this._grid.getSelectionModel().clearSelections();
					this.remuneration(null);
					if(rec){
						this._grid.getSelectionModel().selectRecords([rec]);
					}

				}
			})

		return this._grid;
	},

	getPeriodGrid: function() {
		if(!this._periodGrid)
			this._periodGrid = Ext._create('rh.gfp.remunerationbase.RemunerationPeriodGrid', {
				region: 'center',
				// values: {remuneration: this.remuneration(),},
				// params: {end_validity: null},
				// disabled: true,
				gridAutoLoad: true,

				// region: 'south',
				// gridAutoLoad: false,
				// disabled: true,
				// split: true,
				// allEvent: this,
				// flex: 0.5,
				// height: 400,				
			});

		return this._periodGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
				title: 'Gestor de Bases de remuneração'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					// this.getGrid(),
					this.getPeriodGrid(),
				]
			}
		);

		rh.gfp.remunerationbase.RemunerationBaseManage.superclass.constructor.call(this, cfg);
	},
});
