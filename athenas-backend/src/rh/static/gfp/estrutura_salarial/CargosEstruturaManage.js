/**
 *
 **/

Ext._define('rh.gfp.estrutura_salarial.CargosEstruturaManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.estrutura_salarial.CargosEstruturaGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Cargos/Referências'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.estrutura_salarial.CargosEstruturaManage.superclass.constructor.call(this, cfg);
	}
});
