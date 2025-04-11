/**
 *
 **/

Ext._define('rh.configsalaryprogression.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.configsalaryprogression.Grid', {
				region: 'center'
			});
		return this._grid;
	},

	constructor: function(cfg) {
		try{
			cfg = cfg ? cfg : {};

			Ext.apply(
				cfg,
				{
				    title: 'Gestor de Configurações de Progressão',
					layout: 'border',
					items: this.getGrid()
				}
			);
			rh.configsalaryprogression.Manage.superclass.constructor.call(this, cfg);
		}catch(err){console.info(err)}

	}
});
