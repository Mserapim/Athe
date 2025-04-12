/**
 *
 **/

Ext._define('rh.gfp.paycheck.MarginConsignableManage', {
	extend: 'toolkit.widget.TabPanel',

	margin: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._margin = value;

			if(dispatch) this.observeMargin();
		}
		else
			return this._margin;
	},

	observeMargin: function() {
		if(this.margin()){
			this.getMarginPaychecks().enable();
			this.getMarginPaychecks().setParam('margin', this.margin());
			this.getMarginPaychecks().setFilterProperty('margin', this.margin(), 100);
		}
		else{
			this.getMarginPaychecks().disable();
			this.getMarginPaychecks().getStore().removeAll();
			this.getMarginPaychecks().setFilterProperty('margin', 0, 100, false);
		}
	},

	getMarginGrid: function() {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.paycheck.MarginConsignableGrid', {
				region: 'center',
                
				hideColumns:['active', ],
			});

			// this._grid.getSelectionModel().on({
			// 	scope: this,
			// 	rowselect: function(grid, index, record) {
			// 		this.margin(record.get('pk'));
			// 	},
			// 	rowdeselect: function(grid, index, record){
			// 		this.margin(null);
			// 	}
			// });
		}

		return this._grid;
	},

	// getMarginPaychecks: function() {
	//     if(!this._diff)
	//         this._diff = Ext._create('rh.gfp.paycheck.MarginPaycheckGrid', {
	//         	title: 'Histórico de Margens',
	// 			gridAutoLoad: false,
	// 			flex: 0.5,
	// 			// hideColumns: ['paycheck_unicode',]
	//         });
	
	//     return this._diff;
	// },

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Margens'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
					// bodyStyle: 'padding:15px'
				},				
				items:[
					this.getMarginGrid(),
					// this.getMarginPaychecks(),
				]
			}
		);

		rh.gfp.paycheck.MarginConsignableManage.superclass.constructor.call(this, cfg);
		// this.observeMargin();
	}
});
