/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.EstruturaSalarialManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.estrutura_salarial.EstruturaSalarialGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Estruturas Salariais'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.estrutura_salarial.EstruturaSalarialManage.superclass.constructor.call(this, cfg);
	}
});
