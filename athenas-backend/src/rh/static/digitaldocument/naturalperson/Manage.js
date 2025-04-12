/**
 *
 **/

Ext._define('rh.digitaldocument.naturalperson.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.digitaldocument.naturalperson.Grid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Doc. Digital de Doc. Pessoa Física '
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.digitaldocument.naturalperson.Manage.superclass.constructor.call(this, cfg);
	}
});
