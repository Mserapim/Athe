Ext._define('rh.lista_antiguidade_membros.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getListaAntiguidadeMembrosGrid: function(cfg) {
		if(!this._eventGrid){
			this._eventGrid = Ext._create('rh.lista_antiguidade_membros.Grid', {
				region: 'center',
			});
		}
		return this._eventGrid;
	},

	constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Lista Antiguidade Membros'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				defaults: {
					split: true,
				},
				items:[
					this.getListaAntiguidadeMembrosGrid(cfg),
				]
			}
		);

		rh.lista_antiguidade_membros.Manage.superclass.constructor.call(this, cfg);
	}
});
