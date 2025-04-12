/**
 *
 **/

Ext._define('rh.telefone.TelefoneManage', {
	extend: 'toolkit.widget.TabPanel',

	title: 'Gestor de telefones',

	gridClassName: 'rh.telefone.TelefoneGrid',

	getGrid: function() {
		if (!this._grid) {
			this._grid = Ext._create(this.gridClassName, {
				region: 'center'
			});
		}

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg || {};

		Ext.apply(cfg, {
			layout: 'border',
			items: this.getGrid(),
		});

		rh.telefone.TelefoneManage.superclass.constructor.call(this, cfg);
	}
});
