/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.ReferenciaSalarioManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.estrutura_salarial.ReferenciaSalarioGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Referências Salariais'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.estrutura_salarial.ReferenciaSalarioManage.superclass.constructor.call(this, cfg);
	}
});
