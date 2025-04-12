Ext._define('nomeacao.cadastramento.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('nomeacao.cadastramento.Grid', {
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
			   title: 'Convidados à Nomeação'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		nomeacao.cadastramento.Manage.superclass.constructor.call(this, cfg);
	}
});