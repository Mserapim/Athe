/**
 *
 **/

Ext._define('rh.deficiencyinformation.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.deficiencyinformation.Grid', {
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
			   title: 'Gestor de Deficiências'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.deficiencyinformation.Manage.superclass.constructor.call(this, cfg);
	}
});
