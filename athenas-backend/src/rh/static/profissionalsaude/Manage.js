/**
 *
 **/

Ext._define('rh.profissionalsaude.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.profissionalsaude.Grid', {
				region: 'center',
				hideItemsToolbar: ['remove'],
				hideActions: ['remove'],
				allowRemove: false
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Profissional de Saúde'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.profissionalsaude.Manage.superclass.constructor.call(this, cfg);
	}
});
