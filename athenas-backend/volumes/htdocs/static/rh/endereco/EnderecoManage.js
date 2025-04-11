/**
 *
 **/

Ext._define('rh.endereco.EnderecoManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.endereco.EnderecoGrid', {
				region: 'center',
				hideItemsToolbar: ['remove'],
                hideActions: ['remove'],
                allowRemove: false
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Endereços'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.endereco.EnderecoManage.superclass.constructor.call(this, cfg);
	}
});
