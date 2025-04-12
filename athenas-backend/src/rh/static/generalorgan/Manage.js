/**
 *
 **/

Ext._define('rh.generalorgan.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.generalorgan.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Órgãos Gerais'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.generalorgan.Manage.superclass.constructor.call(this, cfg);
	}
});
