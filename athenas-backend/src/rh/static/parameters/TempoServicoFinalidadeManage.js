/**
 *
 **/

Ext._define('rh.parameters.TempoServicoFinalidadeManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.parameters.TempoServicoFinalidadeGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Tempo Serviço Finalidade'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.parameters.TempoServicoFinalidadeManage.superclass.constructor.call(this, cfg);
	}
});
