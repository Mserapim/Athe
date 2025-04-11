Ext._define('rh.gfp.paycheckdifference.difference_payroll.difference.Manage', {
	extend: 'toolkit.widget.TabPanel',

    getDifferenceGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gfp.paycheckdifference.difference_payroll.difference.Grid', {
				region: 'center',
				gridAutoLoad: false,
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
			   title: 'Diferenças'
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
					this.getDifferenceGrid(cfg),
				]
			}
		);

		rh.gfp.paycheckdifference.difference_payroll.difference.Manage.superclass.constructor.call(this, cfg);
	}
});
