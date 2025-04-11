Ext._define('rh.teletrabalho.gestor_relatorio_semestral.servidor.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('rh.teletrabalho.gestor_relatorio_semestral.servidor.Grid', {
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
			   title: 'Servidor'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);

		rh.teletrabalho.gestor_relatorio_semestral.servidor.Manager.superclass.constructor.call(this, cfg);
	}
});
