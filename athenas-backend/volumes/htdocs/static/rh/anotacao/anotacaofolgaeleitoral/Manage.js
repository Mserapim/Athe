/**
 *
 **/

Ext._define('rh.anotacao.anotacaofolgaeleitoral.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.anotacao.anotacaofolgaeleitoral.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Anotação Folga Eleitoral'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.anotacao.anotacaofolgaeleitoral.Manage.superclass.constructor.call(this, cfg);
	}
});
