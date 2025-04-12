/**
 *
 **/

Ext._define('rh.gfp.accountplan.PlanManage', {
	extend: 'toolkit.widget.TabPanel',

	plan: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._plan = value;

			if(dispatch) this.observePlan();
		}
		else
			return this._plan;
	},

	observePlan: function() {
		if(this.plan()){
			this.getAccountPlan().enable();
			this.getAccountPlan().setParam('plano', this.plan());
			this.getAccountPlan().setFilterProperty('plano_id', this.plan(), 100);
		}
		else{
			this.getAccountPlan().disable();
			this.getAccountPlan().getStore().removeAll();
			this.getAccountPlan().setFilterProperty('plano_id', 0, 100, false);
		}
	},

	getGrid: function() {
		if(!this._planGrid){
			this._planGrid = Ext._create('rh.gfp.accountplan.PlanGrid', {
				region: 'center',
				minHeight: 300,
			});

			this._planGrid.getStore().on({
				scope: this,
				load: function(){
					this.plan(null);
				}

			});

			this._planGrid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.plan(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.plan(null);
				},
			});
		}

		return this._planGrid;
	},

	getAccountPlan: function() {
	    if(!this._faixaGrid)
	        this._faixaGrid = Ext._create('rh.gfp.accountplan.AccountPlanGrid', {
	        	id: 'rh.gfp.accountplan.AccountPlanGrid',
	        	region: 'south',
				minHeight: 300,
				height: 400,
				split: true,
				gridAutoLoad: false
	        });
	
	    return this._faixaGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Plano de Contas (Restful)'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGrid(),
					this.getAccountPlan()
				] 
			}
		);

		rh.gfp.accountplan.PlanManage.superclass.constructor.call(this, cfg);
		this.observePlan();
	}
});
