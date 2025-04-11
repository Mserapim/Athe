/**
 *
 **/

Ext._define('rh.gfp.irrf.IRRFManage', {
	extend: 'toolkit.widget.TabPanel',

	irrf: function(value, dispatch){
		console.debug('VALUE:'+value);
		
		dispatch = core.nullValue(dispatch, true)

		if(value !== undefined){
			this._irrf = value;

			if(dispatch) this.observerIRRF();
		}
		else
			return this._irrf;
	},

	observerIRRF: function(){
		console.debug('observerIRRF: '+this._irrf);
		if(this.irrf()){
			this.getRangeGrid().enable();
			this.getRangeGrid().setParam('irrf', this.irrf());
			this.getRangeGrid().setFilterProperty('irrf_id', this.irrf(), 100);
		}
		else{
			this.getRangeGrid().disable();
			this.getRangeGrid().getStore().removeAll();
			this.getRangeGrid().setFilterProperty('irrf_id', 0, 100, false);
		}
	},

	getIRRFGrid: function() {
		if(!this._irrfGrid)
			this._irrfGrid = Ext._create('rh.gfp.irrf.IRRFGrid', {
	        	region: 'center',
				// width: '60%',
				sm: new Ext.grid.RowSelectionModel({
					singleSelect:true,
					listeners: {
						scope: this,
						rowselect: function(sm, index, data){
							this.irrf(data.get('pk'));
						},
						rowdeselect: function(){ 
							this.irrf(null);
						},						
					}
				}),
				split: true,
			});
			
			this._irrfGrid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					this.irrf(null);
				},
			});			
		return this._irrfGrid;
	},

	getRangeGrid: function(){
		if(!this._rangesGrid){
			this._rangesGrid = Ext._create('rh.gfp.irrf.IRRFFaixaGrid', {
				region: 'south',
				height: 400,
				split: true,
				gridAutoLoad: false,
				// hideItemsToolbar: ['search',],
				hideColumns: ['unicode'] // 'irrf_unicode',
			});

		}

		return this._rangesGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Tabelas de IRRF'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					// this.getPlanGrid(),
					this.getIRRFGrid(),
					this.getRangeGrid()
				]
			}
		);

		rh.gfp.irrf.IRRFManage.superclass.constructor.call(this, cfg);
	}
});
