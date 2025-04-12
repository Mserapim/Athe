/**
 *
 **/

Ext._define('rh.gfp.provisionplan.ProvisionManagerManage', {
	extend: 'toolkit.widget.TabPanel',

	getProvisionManagerGrid: function() {
		if(!this._provisionmanagergrid){
			this._provisionmanagergrid = Ext._create('rh.gfp.provisionplan.ProvisionManagerGrid', {
				region: 'center',
				// ProvisionsGrid: this.getProvisionGrid(),
			});
		}
		return this._provisionmanagergrid;
	},


	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Provisões'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items:[
					this.getProvisionManagerGrid()
				]
			}
		);

		rh.gfp.provisionplan.ProvisionManagerManage.superclass.constructor.call(this, cfg);
	}
});
