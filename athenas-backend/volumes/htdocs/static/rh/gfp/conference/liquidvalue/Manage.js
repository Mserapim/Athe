Ext._define('rh.gfp.conference.liquidvalue.Manage', {
	extend: 'toolkit.widget.TabPanel',

	paycheck: function(value, dispatch){
		dispatch = core.nullValue(dispatch, true);
		if(value !== undefined){
			this._paycheck = value;
		}
		else
			return this._paycheck;
	},

    getPayCheckGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.conference.liquidvalue.Grid', {
				region: 'center',
				gridAutoLoad: false,
				hideColumns: [
					'folha_unicode',
				],
				sm: new Ext.grid.RowSelectionModel({singleSelect: false}),
				doubleClickHandler: function(grid) { },
			});

			this._grid.getSelectionModel().on({
				scope: this,
				beforerowselect: function(grid){
					return true
				},
				rowselect: function(grid, index, record) {
					this.paycheck(record.data);
				},
				rowdeselect: function(grid, index, record){
					this.paycheck(null);
				}
			});

			this._grid.getStore().on({
				scope: this,
				beforeload: function(st, options){
					rec = this._grid.getSelectionModel().getSelected();
					this._grid._lastPaycheck = rec? rec.data.pk: null;
				},
				load: function(st, records, options){
					if(!records.length)
					    this.paycheck(null);

				}
			});
		}

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Valor Líquido (ContraCheque x Rúbrica)'
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
					this.getPayCheckGrid(cfg),
				]
			}
		);

		rh.gfp.conference.liquidvalue.Manage.superclass.constructor.call(this, cfg);
	}
});
