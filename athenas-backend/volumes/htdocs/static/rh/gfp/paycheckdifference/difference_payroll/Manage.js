 Ext._define('rh.gfp.paycheckdifference.difference_payroll.Manage', {
	extend: 'toolkit.widget.TabPanel',

	event: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._event = value;

			if(dispatch) this.observeEvent();
		}
		else
			return this._event;
	},

	observeEvent: function(){
        var selection = this.getPeriodPayrollGrid().getSelectionModel().getSelections();
		if(this.event() && selection.length == 1){
			this.getDifferenceGrid().enable();
			this.getDifferenceGrid()._event = this.event();
			this.getDifferenceGrid().setParam('period', this.event().pk);
			this.getDifferenceGrid().setFilterProperty('period', this.event().pk, 100);
		}
		else{
			this.getDifferenceGrid().disable();
			this.getDifferenceGrid().getStore().removeAll();
			this.getDifferenceGrid().setFilterProperty('period', 0, 100, false);
		}
    },

	getPeriodPayrollGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gfp.paycheckdifference.difference_payroll.Grid', {
				region: 'center',
				extraConf: cfg.folhas,
				gridAutoLoad: true,
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
				doubleClickHandler: function(grid) { },
			});

			this._eventGrid.getSelectionModel().on({
				scope: this,
				beforerowselect: function(eventGrid){
					return true
				},
				rowselect: function(eventGrid, index, record){
					this.event(record.data);
				},
				rowdeselect: function(eventGrid, index, record){
					this.event(null);
				},
			});
	
			this._eventGrid.getStore().on({
				scope: this,
				beforeload: function(st, options){
					rec = this._eventGrid.getSelectionModel().getSelected();
					this._eventGrid._lastEvent = rec? rec.data.pk: null;
				},
				load: function(st, records, options){
					if(!records.length)
						this.event(null);
				}
			});
		}

		return this._eventGrid;
	},

	getDifferenceGrid: function(cfg) {
		if(!this._paychecks)
			this._paychecks = Ext._create('rh.gfp.paycheckdifference.difference_payroll.difference.Grid', {
				region: 'south',
				gridAutoLoad: false,
				disabled: true,
				split: true,
				flex: 0.5,
				height: 400,
				hideColumns:[],
                viewConfig: {
                    stripeRows: false,
				},
				extraConf: cfg.folhas
			});

		return this._paychecks;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gerenciamento das Diferenças de Folha'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
				},
				items:[
					this.getPeriodPayrollGrid(cfg),
					this.getDifferenceGrid(cfg),
				]
			}
		);

		rh.gfp.paycheckdifference.difference_payroll.Manage.superclass.constructor.call(this, cfg);
	}
});
