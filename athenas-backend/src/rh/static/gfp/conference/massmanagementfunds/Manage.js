/**
 *
 **/

 Ext._define('rh.gfp.conference.massmanagementfunds.Manage', {
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
        var selection = this.getEventGrid().getSelectionModel().getSelections();
		if(this.event() && selection.length == 1){
			this.getPayCheckGrid().enable();
			this.getPayCheckGrid()._event = this.event();
			this.getPayCheckGrid()._payroll = this.getEventGrid().payroll();
			this.getPayCheckGrid().setParam('folha', this.getEventGrid().payroll().pk);
			this.getPayCheckGrid().setFilterProperty('folha', this.getEventGrid().payroll().pk, 100);
			this.getPayCheckGrid().setParam('evento', this.event().pk);
			this.getPayCheckGrid().setFilterProperty('evento', this.event().pk, 100);
		}
		else{
			this.getPayCheckGrid().disable();
			this.getPayCheckGrid().getStore().removeAll();
			this.getPayCheckGrid()._event = null;
			this.getPayCheckGrid()._payroll = null;
			this.getPayCheckGrid().setFilterProperty('folha', 0, 100, false);
			this.getPayCheckGrid().setFilterProperty('evento', 0, 100, false);
		}
    },

	getEventGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gfp.conference.massmanagementfunds.Grid', {
				region: 'center',
				gridAutoLoad: false,
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

	getPayCheckGrid: function(cfg) {
		if(!this._paychecks)
			this._paychecks = Ext._create('rh.gfp.conference.massmanagementfunds.folhaevento.Grid', {
				region: 'south',
				configOrderToolBar: ['->', 'download'],
				gridAutoLoad: false,
				disabled: true,
				split: true,
				flex: 0.5,
				height: 400,
				hideColumns:[],
                viewConfig: {
                    stripeRows: false,
				},
			});

		return this._paychecks;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gerenciamento em Massa de Verbas'
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
					this.getEventGrid(cfg),
					this.getPayCheckGrid(cfg),
				]
			}
		);

		rh.gfp.conference.massmanagementfunds.Manage.superclass.constructor.call(this, cfg);
	}
});
