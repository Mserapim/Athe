Ext._define('rh.gfp.gcpp_est_res.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGcppGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gfp.gcpp_est_res.Grid', {
				region: 'center',
				verbas: cfg.verbas,
			});
		}

		return this._eventGrid;
	},

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestão de Controle de Faltas - Estagiários e Residentes'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getGcppGrid(cfg),
				]
			}
		);

		rh.gfp.gcpp_est_res.Manage.superclass.constructor.call(this, cfg);
	}
});
