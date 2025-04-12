/**
 *
 **/

Ext._define('rh.administrativeunit.config.establishment.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.administrativeunit.config.establishment.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de configurações de Estabelecimento'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.administrativeunit.config.establishment.Manage.superclass.constructor.call(this, cfg);
	}
});
