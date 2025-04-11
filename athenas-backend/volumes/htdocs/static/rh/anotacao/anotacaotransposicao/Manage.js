/**
 *
 **/

Ext._define('rh.anotacao.anotacaotransposicao.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.anotacao.anotacaotransposicao.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Anotação Transposição'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.anotacao.anotacaotransposicao.Manage.superclass.constructor.call(this, cfg);
	}
});
