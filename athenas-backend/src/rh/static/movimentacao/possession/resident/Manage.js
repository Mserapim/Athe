/**
 *
 **/

Ext._define('rh.movimentacao.possession.resident.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.movimentacao.possession.resident.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Posses de Residentes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.movimentacao.possession.resident.Manage.superclass.constructor.call(this, cfg);
	}
});
