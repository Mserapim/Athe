
Ext._define('rh.gfp.conference.payroll.EntriesManage', {
	extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.conference.payroll.EntriesGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Eventos/Rubricas'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.conference.payroll.EntriesManage.superclass.constructor.call(this, cfg);
	}


});
