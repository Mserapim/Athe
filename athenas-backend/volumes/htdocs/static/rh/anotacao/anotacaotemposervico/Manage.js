/**
 *
 **/

Ext._define('rh.anotacao.anotacaotemposervico.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.anotacao.anotacaotemposervico.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Anotação Tempo Serviço/Contribuição'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.anotacao.anotacaotemposervico.Manage.superclass.constructor.call(this, cfg);
	}
});
