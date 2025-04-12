/**
 *
 **/

Ext._define('rh.gfp.provisionplan.ProvisionPlanManage', {
	extend: 'toolkit.widget.TabPanel',

	// provisionPlan: function(value, dispatch){
	// 	dispatch = core.nullValue(dispatch, true);

	// 	if(value !== undefined){
	// 		this._provisionPlan = value;

	// 		if(dispatch) this.observeProvisionPlan();
	// 	}
	// 	else
	// 		return this._provisionPlan;
	// },

	provisionManager: function(value, dispatch){
		console.debug('VALUE:'+value);
		
		dispatch = core.nullValue(dispatch, true)

		if(value !== undefined){
			this._provisionManager = value;

			if(dispatch) this.observerProvisionManager();
		}
		else
			return this._provisionManager;
	},

	// observeProvisionPlan: function() {
	// 	if(this.provisionPlan()){
	// 		this.getProvisionManagerGrid().enable();
	// 		this.getProvisionManagerGrid().setParam('provision_plan', this.provisionPlan());
	// 		this.getProvisionManagerGrid().setFilterProperty('provision_plan_id', this.provisionPlan(), 100);
	// 	}
	// 	else{
	// 		this.getProvisionManagerGrid().disable();
	// 		this.getProvisionManagerGrid().getStore().removeAll();
	// 		this.getProvisionManagerGrid().setFilterProperty('provision_plan_id', 0, 100, false);
	// 	}
	// },

	observerProvisionManager: function(){
		console.debug('observerProvisionManager: '+this._provisionManager);
		if(this.provisionManager()){
			this.getProvisionGrid().enable();
			this.getProvisionGrid().setParam('provision_manager', this.provisionManager());
			this.getProvisionGrid().setFilterProperty('provision_manager_id', this.provisionManager(), 100);
		}
		else{
			this.getProvisionGrid().disable();
			this.getProvisionGrid().getStore().removeAll();
			this.getProvisionGrid().setFilterProperty('provision_manager_id', 0, 100, false);
		}
	},

	// getPlanGrid: function() {
	// 	if(!this._gridPlan)
	// 		this._gridPlan = Ext._create('rh.gfp.provisionplan.ProvisionPlanGrid', {
	// 			region: 'center',
	// 			hideItemsToolbar: ['edit', 'remove', 'search'],
	// 			sm: new Ext.grid.RowSelectionModel({
	// 				singleSelect:true,
	// 				listeners: {
	// 					scope: this,
	// 					rowselect: function(sm, index, data){
	// 						this.provisionPlan(data.get('pk'));
	// 					},
	// 					rowdeselect: function(){
	// 						this.provisionPlan(null);
	// 					},						
	// 				}
	// 			}),
	// 			hideColumns: ['provision_plan_unicode', ],
	// 		});

	// 		this._gridPlan.getStore().on({
	// 			scope: this,
	// 			beforeload: function(gd, opts){
	// 				this.provisionPlan(null);
	// 			}
	// 		});

	// 	return this._gridPlan;
	// },

	getProvisionManagerGrid: function() {
		if(!this._provisionManagerGrid)
			this._provisionManagerGrid = Ext._create('rh.gfp.provisionplan.ProvisionManagerGrid', {
	        	region: 'center',
				// width: '60%',
				sm: new Ext.grid.RowSelectionModel({
					singleSelect:true,
					listeners: {
						scope: this,
						rowselect: function(sm, index, data){
							this.provisionManager(data.get('pk'));
						},
						rowdeselect: function(){ 
							this.provisionManager(null);
						},						
					}
				}),
				split: true,
				// values: {provision_plan: this.provisionPlan(),},
				// disabled: true,
				// gridAutoLoad: false			
			});
			
			this._provisionManagerGrid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					this.provisionManager(null);
				},
			});			
		return this._provisionManagerGrid;
	},

	getProvisionGrid: function(){
		if(!this._provisionsgrid){
			this._provisionsgrid = Ext._create('rh.gfp.provisionplan.ProvisionGrid', {
				region: 'south',
				height: 400,
				split: true,
				gridAutoLoad: false,
				// hideItemsToolbar: ['search',],
				hideColumns: ['provision_manager_unicode', ]
			});

		}

		return this._provisionsgrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Provisões'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					// this.getPlanGrid(),
					this.getProvisionManagerGrid(),
					this.getProvisionGrid()
				]
			}
		);

		rh.gfp.provisionplan.ProvisionPlanManage.superclass.constructor.call(this, cfg);
	}
});
