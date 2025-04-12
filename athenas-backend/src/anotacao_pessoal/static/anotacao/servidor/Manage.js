/**
 *
 **/

Ext._define('anotacao_pessoal.anotacao.servidor.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('anotacao_pessoal.anotacao.servidor.Grid', {
				region: 'center',
				cfg: cfg,
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Servidor'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);

		anotacao_pessoal.anotacao.servidor.Manager.superclass.constructor.call(this, cfg);
	}
});
