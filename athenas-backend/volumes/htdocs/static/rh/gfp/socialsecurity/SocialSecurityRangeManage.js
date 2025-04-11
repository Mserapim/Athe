/**
 *
 **/

Ext._define('rh.gfp.socialsecurity.SocialSecurityRangeManage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function() {
		if(!this._grid)
			this._grid = Ext._create('rh.gfp.socialsecurity.SocialSecurityRangeGrid', {
				region: 'center'
			});

		return this._grid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Previdência Social/Privada'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid()
			}
		);

		rh.gfp.socialsecurity.SocialSecurityRangeManage.superclass.constructor.call(this, cfg);
	}
});
