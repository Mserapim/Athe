Ext._define('rh.gfp.familysalary.Manage', {
	extend: 'toolkit.widget.TabPanel',

	salary: function(value, dispatch){
		console.debug('VALUE:'+value);
		
		dispatch = core.nullValue(dispatch, true)

		if(value !== undefined){
			this._salary = value;

			if(dispatch) this.observerSalary();
		}
		else
			return this._salary;
	},

	observerSalary: function(){
		console.debug('observer: '+this._salary);
		if(this.salary()){
			this.getRangeGrid().enable();
			this.getRangeGrid().setParam('family_salary', this.salary());
			this.getRangeGrid().setFilterProperty('family_salary_id', this.salary(), 100);
		}
		else{
			this.getRangeGrid().disable();
			this.getRangeGrid().getStore().removeAll();
			this.getRangeGrid().setFilterProperty('family_salary_id', 0, 100, false);
		}
	},

	getFamilySalaryGrid: function() {
		if(!this._familySalaryGrid)
			this._familySalaryGrid = Ext._create('rh.gfp.familysalary.FamilySalaryGrid', {
	        	region: 'center',
				// width: '60%',
				sm: new Ext.grid.RowSelectionModel({
					singleSelect:true,
					listeners: {
						scope: this,
						rowselect: function(sm, index, data){
							this.salary(data.get('pk'));
						},
						rowdeselect: function(){ 
							this.salary(null);
						},						
					}
				}),
				split: true,
			});
			
			this._familySalaryGrid.getStore().on({
				scope: this,
				beforeload: function(gd, opts){
					this.salary(null);
				},
			});			
		return this._familySalaryGrid;
	},

	getRangeGrid: function(){
		if(!this._rangesGrid){
			this._rangesGrid = Ext._create('rh.gfp.familysalary.FamilySalaryRangeGrid', {
				region: 'south',
				height: 400,
				split: true,
				gridAutoLoad: false,
				hideColumns: ['unicode']
			});

		}
		
		return this._rangesGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Tabelas de Salário Família'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: [
					this.getFamilySalaryGrid(),
					this.getRangeGrid()
				]
			}
		);

		rh.gfp.familysalary.Manage.superclass.constructor.call(this, cfg);
	}
});
