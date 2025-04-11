Ext._define('rh.teletrabalho.teletrabalho_competencia.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.teletrabalho.teletrabalho_competencia.Grid', {
				region: 'center',
			});
		}

		return this._grid;
	},

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Teletrabalho Competências'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		rh.teletrabalho.teletrabalho_competencia.Manage.superclass.constructor.call(this, cfg);
        
        this.getGrid(cfg).filtroMesAno();
	}
});