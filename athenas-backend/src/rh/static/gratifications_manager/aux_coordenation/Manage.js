Ext._define('rh.gratifications_manager.aux_coordenation.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gratifications_manager.aux_coordenation.Grid', {
				region: 'center',
				
				doubleClickHandler: function(cfg) {
					var gratAuxCoordId = cfg.selModel.selections.items[0].json.grat_aux_coord_id;
					if(gratAuxCoordId){
						Ext._create('rh.gratifications_manager.aux_coordenation.gratificacao.Window', {
							gratAuxCoordId: gratAuxCoordId,
							callback: {
								success: { scope: this, fn: function() { this.getStore().reload(); }}
							}
						}).show();
					}else{
						Ext.Msg.show({
							title: this.title,
							icon: Ext.Msg.INFO,
							buttons: Ext.Msg.OK,
							msg: 'Para poder alterar os valores o registro precisa ser calculado.'
						});
					}
				},
			
			});
		}

		return this._grid;
	},

    constructor: function(cfg) {
		cfg = cfg ? cfg : {};

		Ext.applyIf(
			cfg,
			{
			   title: 'Gestor de Designação para Auxiliar de Coordenação'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);

		rh.gratifications_manager.aux_coordenation.Manage.superclass.constructor.call(this, cfg);

        this.getGrid(cfg).filtrarAnoMes();
	}
});