/**
 *
 **/

Ext._define('rh.foreigninformation.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.foreigninformation.Grid', {
				region: 'center',
				hideItemsToolbar: [],
                hideActions: [],
                allowRemove: false
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Informações de Estrangeiro'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.foreigninformation.Manage.superclass.constructor.call(this, cfg);
	}
});
