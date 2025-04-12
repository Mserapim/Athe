/**
 *
 **/

Ext._define('rh.gfp.dirf.DialectManage', {
	extend: 'toolkit.widget.TabPanel',

	dialect: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true)

		if(value !== undefined){
			this._dialect = value;

			if(dispatch) this.observerDialect();
		}
		else
			return this._dialect;
	},

	observerDialect: function(){
		if(this.dialect()){
			this.getTokenGrid().enable();
			this.getTokenGrid().setParam('dialect', this.dialect());
			this.getTokenGrid().setFilterProperty('dialect_id', this.dialect(), 100);
		}
		else{
			this.getTokenGrid().disable();
			this.getTokenGrid().getStore().removeAll();
			this.getTokenGrid().setFilterProperty('dialect_id', 0, 100, false);
		}
	},

	getDialectGrid: function() {
		if(!this._dialectGrid)
			this._dialectGrid = Ext._create('rh.gfp.dirf.DialectGrid', {
	        	region: 'center',
				// width: '60%',
				sm: new Ext.grid.RowSelectionModel({
					singleSelect:true,
					listeners: {
						scope: this,
						rowselect: function(sm, index, data){
							this.dialect(data.get('pk'));
						},
						rowdeselect: function(){ 
							this.dialect(null);
						},						
					}
				}),
				split: true,
			});
			
			this._dialectGrid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					this.dialect(null);
				},
			});			
		return this._dialectGrid;
	},

	getTokenGrid: function(){
		if(!this._tokenGrid){
			this._tokenGrid = Ext._create('rh.gfp.dirf.TokenGrid', {
				region: 'south',
				height: 400,
				split: true,
				gridAutoLoad: false,
				// hideItemsToolbar: ['search',],
				hideColumns: ['unicode'] // 'irrf_unicode',
			});

		}

		return this._tokenGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Configurador DIRF'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					// this.getPlanGrid(),
					this.getDialectGrid(),
					this.getTokenGrid()
				]
			}
		);

		rh.gfp.dirf.DialectManage.superclass.constructor.call(this, cfg);
	}
});
