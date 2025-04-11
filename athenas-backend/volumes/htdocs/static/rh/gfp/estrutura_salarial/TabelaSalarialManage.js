/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.TabelaSalarialManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.estrutura_salarial.TabelaSalarialGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Tabelas Salariais'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.estrutura_salarial.TabelaSalarialManage.superclass.constructor.call(this, cfg);
	}
});
