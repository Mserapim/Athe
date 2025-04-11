/**
 *
 **/

Ext._define('rh.gfp.parameters.RRAManage', {
	extend: 'toolkit.widget.TabPanel',

	getRRAGrid: function() {
		if(!this._rragrid){
			this._rragrid = Ext._create('rh.gfp.parameters.RRAGrid', {
				region: 'center',
				RRAEmployeeGrid: this.getRRAEmployeeGrid(),
			});
		}

		this._rragrid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.rra(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.rra(null);
				},
		});

		return this._rragrid;
	},

	getRRAEmployeeGrid: function(){
		if(!this._rraemployeegrid){
			this._rraemployeegrid = Ext._create('rh.gfp.parameters.RRAEmployeeGrid', {
				region: 'east',
				width: "50%",
				split: true,
				gridAutoLoad: false
			});

		}

		return this._rraemployeegrid;
	},

	rra: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true)

		if(value !== undefined){
			this._rra = value;

			if(dispatch) this.observeRRA();
		}
		else
			return this._rra;
	},

	observeRRA: function(){
		if(this.rra()){
			this.getRRAEmployeeGrid().enable();
			this.getRRAEmployeeGrid().setParam('rra', this.rra());
			this.getRRAEmployeeGrid().setFilterProperty('rra_id', this.rra(), 100);
		}
		else{
			this.getRRAEmployeeGrid().disable();
			this.getRRAEmployeeGrid().getStore().removeAll();
			this.getRRAEmployeeGrid().setFilterProperty('rra_id', 0, 100, false);
		}
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'RRA'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getRRAGrid(),
					this.getRRAEmployeeGrid()
				]
			}
		);

		rh.gfp.parameters.RRAManage.superclass.constructor.call(this, cfg);
		this.observeRRA();

	}
});
