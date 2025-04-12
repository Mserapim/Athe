/**
 *
 **/

Ext._define('rh.socialsecurity.SocialSecurityConfigManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.socialsecurity.SocialSecurityConfigGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Informações de previdência'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.socialsecurity.SocialSecurityConfigManage.superclass.constructor.call(this, cfg);
	}
});
