Ext._define('rh.nomeacao.anexo_nomeacao.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.nomeacao.anexo_nomeacao.Grid', {
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
			   title: 'Anexos Nomeação'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		rh.nomeacao.anexo_nomeacao.Manage.superclass.constructor.call(this, cfg);
	}
});