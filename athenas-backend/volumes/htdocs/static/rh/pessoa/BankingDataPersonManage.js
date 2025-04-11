/**
 *
 **/

Ext._define('rh.pessoa.BankingDataPersonManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.pessoa.BankingDataPersonGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Dado Bancário - Pessoa (Restful)'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.pessoa.BankingDataPersonManage.superclass.constructor.call(this, cfg);
	}
});
