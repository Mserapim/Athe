Ext._define('rh.employeeaccesscontrol.employee.Grid', {
	extend: 'core.RestfulGrid',

	rest: 'rh.employeeaccesscontrol.employee.Restful',

	hideActions: ['copy', 'add', 'edit', 'remove'],

	configOrderToolBar: ['search'],

	getColumnModel: function () {
		if (!this._columnModel)
			this._columnModel = Ext._create(
				'Ext.grid.ColumnModel',
				[
					Ext._create('Ext.grid.RowNumberer'),
					{ header: 'Chave', dataIndex: 'pk', width: 55, hidden: true },
					{
						header: 'Ativo',
						dataIndex: 'ativo',
						width: 70,
						renderer: toolkit.util.formatIconYesNo,
					},
					{ header: 'Matrícula', dataIndex: 'matricula', width: 80, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
					{ header: 'Usuário', dataIndex: 'user_unicode', width: 80 },
					{ header: 'Email', dataIndex: 'email', width: 300 },
					{ header: 'Nome', dataIndex: 'pessoa_fisica_unicode', id: 'autoExpandColumn' },
					{ header: 'Tipo', dataIndex: 'type_by_possession_display', width: 180 },
					{ header: 'Criado por', dataIndex: 'created_by_unicode', width: 90, hidden: true },
					{ header: 'Criação', dataIndex: 'created_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: false, sortable: true },
					{ header: 'Alterado por', dataIndex: 'modified_by_unicode', width: 90, hidden: true },
					{ header: 'Alteração', dataIndex: 'modified_at', width: 120, renderer: Ext.util.Format.dateRenderer('d/m/Y H:i'), hidden: true },
				]
			);
		return this._columnModel;
	},

	execOperation: function(action){
		var selected = this.getSelectionModel().getSelected();

		if (selected) {
			if (action == 'create_user_by_admin'){
				var title = 'Criar Usuário no Athenas'
				var message = 'Tem certeza que deseja criar usúario do Athenas para o(a) servidor(a): <br> <b>' + selected.get('matricula') + ' : ' + selected.get('social_name') + '</b>?'
			}
			if (action == 'create_user_ldap') {
				var title = 'Criar Usuário no LDAP'
				var message = 'Tem certeza que deseja criar usúario do LDAP para o(a) servidor(a): <br> <b>' + selected.get('matricula') + ' : ' + selected.get('social_name') + '</b>?'
			}
			if (action == 'reset_user_password'){
				var title = 'Restaurar a senha  do Servidor'
				var message = 'Tem certeza que deseja resetar senha para o(a) servidor(a): <br> <b>' + selected.get('matricula') + ' : ' + selected.get('social_name') + '</b>?'
			}

			if (selected.get('ativo') == true) {
				Ext.Msg.show({
					title: title,
					icon: Ext.Msg.QUESTION,
					buttons: Ext.Msg.YESNO,
					msg: message,
					scope: this,

					fn: function (button) {
						if (button == 'no') return;
						var params = {
							customAction: action,
							employee: selected.get('pk')
						}

						var teste = this._process(params);
					}
				});
			} else {
				Ext.Msg.show({
					title: title,
					icon: Ext.Msg.ERROR,
					buttons: Ext.Msg.OK,
					msg: 'O servidor está inativo.'
				});
			}
		} else {
			Ext.Msg.show({
				title: title,
				icon: Ext.Msg.ERROR,
				buttons: Ext.Msg.OK,
				msg: 'Selecione 1 servidor para criar o usuário .'
			});
		}
	},

	getOperationAction: function(){
		if(!this._operationAction){
			this._operationAction = Ext._create('Ext.Button', {
				text: 'Acões',
				iconCls: 'icon-edocs icon-protocolo-actions',
				scope: this,
				menu: [
					{
						text: 'Criar Usuário no Athenas',
						iconCls: 'icon-core icon-core-set-employee',
						scope: this,
						handler: function() {
							this.execOperation('create_user_by_admin')
						}
					},
					{
						text: 'Criar Usuário no LDAP',
						iconCls: 'icon-core icon-core-set-employee',
						scope: this,
						handler: function () {
							this.execOperation('create_user_ldap')
						}
					},
					{
						text: 'Restaurar a senha do Servidor',
						iconCls: 'icon-core icon-core-set-employee',
						scope: this,
						handler: function() {
							this.execOperation('reset_user_password')
						}
					},
				],
			});
		}

		return this._operationAction;
	},

	_process: function (params) {
		var rest = Ext._create(this.rest, { resource: this.resource });
		var mask = Ext._create('Ext.LoadMask', this.getEl(), { msg: 'Processando informações.' });
		var wnd = this;

		mask.show();
		rest._process(
			params,
			{
				scope: this,
				fn: function (rst) {
					core.invokeCallback((externalCallback || { fn: Ext.emptyFn }), rst.message);
				}
			},
			{
				fn: function (message) {
					Ext.Msg.show({
						title: 'Informando',
						icon: Ext.Msg.ERROR,
						buttons: Ext.Msg.OK,
						msg: message
					});
				}
			},
			{
				fn: function () {
					mask.hide();
				}
			}
		);
	},
});

core.RestfulGrid.register(
	'rh.employeeaccesscontrol.employee.Restful',
	'rh.employeeaccesscontrol.employee.Grid'
);