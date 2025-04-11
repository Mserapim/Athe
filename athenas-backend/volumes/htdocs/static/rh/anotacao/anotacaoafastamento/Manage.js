/**
 *
 **/

Ext._define('rh.anotacao.anotacaoafastamento.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.anotacao.anotacaoafastamento.Grid', {
				region: 'center',
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Anotação de Afastamento'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.anotacao.anotacaoafastamento.Manage.superclass.constructor.call(this, cfg);
	}
});
