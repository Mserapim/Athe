Ext._define('rh.gestorenvioponto.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gestorenvioponto.Grid', {
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
			   title: 'Gestor de Envio de Folha Ponto'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		rh.gestorenvioponto.Manage.superclass.constructor.call(this, cfg);
        
        this.getGrid(cfg).filtroMesAno();
	}
});