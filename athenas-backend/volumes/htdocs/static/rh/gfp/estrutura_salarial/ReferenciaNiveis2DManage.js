/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.ReferenciaNiveis2DManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.estrutura_salarial.ReferenciaNiveis2DGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Referências do Modelo'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.estrutura_salarial.ReferenciaNiveis2DManage.superclass.constructor.call(this, cfg);
	}
});
