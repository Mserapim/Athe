/**
 *
 **/

Ext._define('rh.anotacao.anotacaoelogio.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.anotacao.anotacaoelogio.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Anotação Elogio'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.anotacao.anotacaoelogio.Manage.superclass.constructor.call(this, cfg);
	}
});
