/**
 *
 **/

Ext._define('rh.movimentacao.possession.reintegration.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.movimentacao.possession.reintegration.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Reintegração'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.movimentacao.possession.reintegration.Manage.superclass.constructor.call(this, cfg);
	}
});
