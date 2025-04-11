 Ext._define('rh.gratifications_manager.member_gratifications.gratificacoes.Manage', {
	extend: 'toolkit.widget.TabPanel',

	getGratificacoesGrid: function(cfg) {
		if(!this._grid)
			this._grid = Ext._create('rh.gratifications_manager.member_gratifications.gratificacoes.Grid');

		return this._grid;
	},

});
