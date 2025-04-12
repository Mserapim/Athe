Ext._define('rh.gratifications_manager.diligence.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGrid: function(cfg) {
		if(!this._grid){
			this._grid = Ext._create('rh.gratifications_manager.diligence.Grid', {
				region: 'center',
				
				doubleClickHandler: function(cfg) {
					var gratDiligenciaId = cfg.selModel.selections.items[0].json.grat_diligencia_id;
					if(gratDiligenciaId){
						Ext._create('rh.gratifications_manager.diligence.gratificacao.Window', {
							gratDiligenciaId: gratDiligenciaId,
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
			   title: 'Designação para Diligência'
			}
		);

		Ext.apply(
			cfg,
			{
				layout: 'border',
				items: this.getGrid(cfg)
			}
		);
		rh.gratifications_manager.diligence.Manage.superclass.constructor.call(this, cfg);
        
        this.getGrid(cfg).filtrarAnoMes();
	}
});