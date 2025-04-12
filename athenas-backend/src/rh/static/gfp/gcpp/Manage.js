Ext._define('rh.gfp.gcpp.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGcppGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.gfp.gcpp.Grid', {
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
			   title: 'GCPP - Gestão de Controle de Pagamento de Pessoas'
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

		rh.gfp.gcpp.Manage.superclass.constructor.call(this, cfg);
	}
});
