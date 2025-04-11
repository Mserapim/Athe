Ext._define('rh.teletrabalho.gestor_relatorio_semestral.gestor.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('rh.teletrabalho.gestor_relatorio_semestral.gestor.Grid', {
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
			   title: 'Gestor'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);

		rh.teletrabalho.gestor_relatorio_semestral.gestor.Manager.superclass.constructor.call(this, cfg);
	}
});
