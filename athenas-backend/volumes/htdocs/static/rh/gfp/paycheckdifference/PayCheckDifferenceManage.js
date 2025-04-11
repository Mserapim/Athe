/**
 *
 **/

Ext._define('rh.gfp.paycheckdifference.PayCheckDifferenceManage', {
	extend: 'toolkit.widget.TabPanel',

	difference: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._difference = value;

			if(dispatch) this.observeDifference();
		}
		else
			return this._difference;
	},

	observeDifference: function() {
		if(this.difference()){
			this.getPayCheckDifferenceItemGrid().enable();
			this.getPayCheckDifferenceItemGrid().setParam('difference', this.difference());
			this.getPayCheckDifferenceItemGrid().setFilterProperty('difference', this.difference(), 100);
			this.getEntryGrid().enable();
			this.getEntryGrid().setParam('paycheck_difference', this.difference());
			this.getEntryGrid().setFilterProperty('paycheck_difference', this.difference(), 100);
		}
		else{
			this.getPayCheckDifferenceItemGrid().disable();
			this.getPayCheckDifferenceItemGrid().getStore().removeAll();
			this.getPayCheckDifferenceItemGrid().setFilterProperty('difference', 0, 100, false);
			this.getEntryGrid().disable();
			this.getEntryGrid().getStore().removeAll();
			this.getEntryGrid().setFilterProperty('paycheck_difference', 0, 100, false);
		}
	},

	getPayCheckDifferenceGrid: function() {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.paycheckdifference.PayCheckDifferenceGrid', {
				region: 'center',
			});

			this._grid.getSelectionModel().on({
				scope: this,
				rowselect: function(grid, index, record) {
					this.difference(record.get('pk'));
					this.getEntryGrid().employee = record.get('employee');
					this.getEntryGrid().genre_event = record.get('genre_event');
				},
				rowdeselect: function(grid, index, record){
					this.difference(null);
					this.getEntryGrid().employee = null;
					this.getEntryGrid().genre_event = null;
				}
			});
		}

		return this._grid;
	},


	getPayCheckDifferenceItemGrid: function() {
	    if(!this._diff)
	        this._diff = Ext._create('rh.gfp.paycheckdifference.PayCheckDifferenceItemGrid', {
	        	title: 'Diferenças',
				gridAutoLoad: false,
				flex: 0.5,
				hideColumns: ['paycheck_unicode',]
	        });
	
	    return this._diff;
	},


	getEntryGrid: function() {
	    if(!this._entry)
	        this._entry = Ext._create('rh.gfp.paycheckdifference.EntriesDifferenceGrid', {
				title: 'Pagamentos',
				gridAutoLoad: false,
				flex: 0.5,
	        });

	    return this._entry;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Diferenças'
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
					this.getPayCheckDifferenceGrid(),
					{
						region: 'south',
                        height: 350,
                        border: false,                        
						layout:'hbox',
						layoutConfig: {
						    align : 'stretch',
						},
						items: [
							this.getPayCheckDifferenceItemGrid(),
							this.getEntryGrid()
						]					
					}
				]
			}
		);

		rh.gfp.paycheckdifference.PayCheckDifferenceManage.superclass.constructor.call(this, cfg);
		this.observeDifference();
	}
});
