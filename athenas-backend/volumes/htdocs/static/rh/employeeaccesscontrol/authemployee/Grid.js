Ext._define('rh.employeeaccesscontrol.authemployee.Grid', {
	extend: 'core.RestfulGrid',

	restWindow: 'rh.employeeaccesscontrol.authemployee.Window',

	hideActions: ['copy', 'add', 'remove'],

	configOrderToolBar: ['edit', 'search'],

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
						width: 45,
						renderer: toolkit.util.formatIconYesNo,
					},
					{ header: 'Matrícula', dataIndex: 'matricula', width: 65, renderer: function (value) { return '<div style="text-align:right">' + value + '</div>'; } },
					{ header: 'Usuário', dataIndex: 'user_unicode', width: 70 },
					{ header: 'Email', dataIndex: 'email', width: 250 },
					{ header: 'Nome', dataIndex: 'pessoa_fisica_unicode', id: 'autoExpandColumn' },
					{ header: 'Status do usuário', dataIndex: 'is_active', width: 60, renderer: toolkit.util.formatIconYesNo },
					{ header: 'Membro de equipe', dataIndex: 'is_staff', width: 60, renderer: toolkit.util.formatIconYesNo },
					{ header: 'Administrador', dataIndex: 'is_superuser', width: 60, renderer: toolkit.util.formatIconYesNo },
					{ header: 'E-mail pessoal verificado?', dataIndex: 'email_pessoal_verificado', width: 80, renderer: toolkit.util.formatIconYesNo },
					{ header: 'Verificado no Mastiff?', dataIndex: 'verificado_mastiff', hidden: true, width: 60, renderer: toolkit.util.formatIconYesNo },
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

	_realizarReq: function(params, nome_classe, nome_metodo){
        Ext.Ajax.request({
            url: toolkit.util.Normalize.controller_action(nome_classe,nome_metodo),
            params: params,
            success: function(request) {
                var obj = Ext.decode(request.responseText);
                var icon = obj.success == true ? Ext.Msg.INFO : Ext.Msg.ERROR;
                Ext.Msg.show({
                    width:"400px",
                    title: this.title,
                    icon: icon,
                    buttons: Ext.Msg.OK,
                    msg: obj.message
                });
                if(obj.success == true){ this.getStore().reload(); }
            },
            failure: function() {
                Ext.Msg.show({
                    title: this.title,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponivel no momento, tente novamente mais tarde.'
                });
            },
            scope: this
        });
    },

	atualizarMastiff: function(usuario_infos){
		Ext.Msg.show({
			msg: "Tem certeza que deseja atualizar os dados do usuário (username e email) através do Mastiff?",
			icon: Ext.Msg.QUESTION,
			buttons: Ext.Msg.YESNO,
			scope: this,
			fn: function (b) {
				if (b == 'no') return;

				params = {'matricula': usuario_infos.matricula};
				this._realizarReq(params, 'AUTHEmployeeRestful', 'atualizar_infos_usuario_mastiff');
			}
		});
    },

	getConfigCustomActions: function(){
        return [
            {
                iconCls: 'icon-16px icon-core icon-core-run',
                tooltip: 'Atualizar pelo Mastiff',
                scope: this,
                handler: function(action, index){ this.atualizarMastiff(action._store.getAt(index).data); },
            },
        ];
    },

});

core.RestfulGrid.register(
	'rh.employeeaccesscontrol.authemployee.Restful',
	'rh.employeeaccesscontrol.authemployee.Grid'
);