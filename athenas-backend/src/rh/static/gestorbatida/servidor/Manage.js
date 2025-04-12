Ext._define('rh.gestorbatida.servidor.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('rh.gestorbatida.servidor.Grid', {
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

		rh.gestorbatida.servidor.Manager.superclass.constructor.call(this, cfg);
	}
});
