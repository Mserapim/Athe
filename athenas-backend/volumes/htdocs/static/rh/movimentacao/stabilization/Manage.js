/**
 *
 **/

Ext._define('rh.movimentacao.stabilization.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.movimentacao.stabilization.Grid', {
				region: 'center',
				hideItemsToolbar: ['add', 'remove'],
				hideActions: ['add', 'remove', 'copy']
			});
		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Estabilizações'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.movimentacao.stabilization.Manage.superclass.constructor.call(this, cfg);
	}
});
