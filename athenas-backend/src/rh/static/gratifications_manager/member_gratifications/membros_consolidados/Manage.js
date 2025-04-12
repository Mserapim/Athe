 Ext._define('rh.gratifications_manager.member_gratifications.membros_consolidados.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getExercCumulConsolidadoGrid: function(cfg) {
		if(!this._exerc_cumul_perm)
			this._exerc_cumul_perm = Ext._create('rh.gratifications_manager.member_gratifications.membros_consolidados.Grid');

		return this._exerc_cumul_perm;
	},

});
