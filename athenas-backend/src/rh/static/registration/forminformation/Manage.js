Ext._define('rh.registration.forminformation.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid){
			this._grid = Ext._create('rh.registration.forminformation.Grid', {
				region: 'center'
			});

			this._grid.getSelectionModel().on({
				scope: this,
				rowselect: function(sm, index, data){
					this.forminformation(data.get('pk'));
				},
				rowdeselect: function(){ 
					this.forminformation(null);
				},
			});
		}


		return this._grid;
	},

	forminformation: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);

		if(value !== undefined){
			this._forminformation = value;

			if(dispatch) this.observeForm();
		}
		else
			return this._forminformation;
	},

	getValidation: function() {
	    if(!this._validationGrid)
	        this._validationGrid = Ext._create('rh.registration.forminformation.validation.Grid', {
	        	region: 'south',
				minHeight: 300,
				height: 400,
				split: true,
				gridAutoLoad: false,
				disabled: true
	        });	
	    return this._validationGrid;
	},


	observeForm: function() {
		if(this.forminformation()){
			this.getValidation().enable();
			this.getValidation().setParam('form_information', this.forminformation());
			this.getValidation().setFilterProperty('form_information_id', this.forminformation(), 100);
		}
		else{
			this.getValidation().disable();
			this.getValidation().getStore().removeAll();
			this.getValidation().setFilterProperty('form_information_id', 0, 100, false);
		}
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Formulário de Dados Pessoais'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGrid(),
					this.getValidation()
				]
			}
		);

		rh.registration.forminformation.Manage.superclass.constructor.call(this, cfg);
		this.observeForm();
	}
});
